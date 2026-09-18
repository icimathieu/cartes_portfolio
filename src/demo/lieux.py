"""
Vérification des noms de lieux contre le référentiel officiel des communes.

Le modèle confond parfois les niveaux : sur une carte de « FONTAINE DE VAUCLUSE
— La Place », il a répondu commune « Vaucluse » et monument « Fontaine de
Vaucluse ». Le référentiel permet de rattraper ce cas sans base de connaissances
patrimoniale : on sait quels noms sont des communes et lesquels sont des
départements, donc on sait quel niveau est le bon.

Attention, la vérification ne peut pas être naïve : « Vaucluse » est à la fois
un département et une commune du Doubs. On ne corrige donc que lorsque deux
niveaux se contredisent, jamais sur un nom isolé — une règle qui écartait la
commune dès qu'elle portait le nom du département a été retirée après mesure :
elle perdait deux cartes sur le jeu de référence et n'en gagnait aucune.

Le référentiel vient des communes de France (INSEE / La Poste, données
ouvertes), réduit à ce qui sert ici : nom, département, coordonnées.
"""

import csv
import unicodedata
from pathlib import Path

RACINE_ASSETS = Path("assets/referentiel")
FICHIER_COMMUNES = "communes_france.csv"
FICHIER_DEPARTEMENTS = "departements_france.csv"

_communes = None
_departements = None
_codes_departements = None


def normaliser(valeur):
    """« Fontaine-de-Vaucluse » et « FONTAINE DE VAUCLUSE » donnent la même clé."""
    if not valeur:
        return ""
    texte = unicodedata.normalize("NFKD", str(valeur)).encode("ascii", "ignore").decode()
    texte = texte.lower()
    return " ".join("".join(c if c.isalnum() else " " for c in texte).split())


def _charger():
    global _communes, _departements, _codes_departements
    if _communes is not None:
        return
    _communes, _departements, _codes_departements = {}, {}, {}
    chemin = RACINE_ASSETS / FICHIER_COMMUNES
    if chemin.exists():
        with chemin.open(encoding="utf-8") as flux:
            for ligne in csv.DictReader(flux):
                _communes.setdefault(ligne["cle"], []).append({
                    "nom": ligne["nom"],
                    "departement": ligne["departement"],
                    "lat": float(ligne["latitude"]) if ligne["latitude"] else None,
                    "lon": float(ligne["longitude"]) if ligne["longitude"] else None,
                })
    chemin = RACINE_ASSETS / FICHIER_DEPARTEMENTS
    if chemin.exists():
        with chemin.open(encoding="utf-8") as flux:
            for ligne in csv.DictReader(flux):
                _departements[ligne["cle"]] = ligne["nom"]
                _codes_departements[ligne["cle"]] = ligne.get("code", "")


def est_commune(nom):
    _charger()
    return normaliser(nom) in _communes


def est_departement(nom):
    _charger()
    return normaliser(nom) in _departements


def nom_officiel(nom, departement=None):
    """Orthographe officielle de la commune, ou le nom d'origine."""
    entrees = _entrees(nom, departement)
    return entrees[0]["nom"] if entrees else nom


def _entrees(nom, departement=None):
    """Communes portant ce nom, restreintes au département imprimé sur la carte.

    Si le nom n'existe pas dans ce département, on ne renvoie rien : « Pernes »
    est une commune du Pas-de-Calais, mais sur une carte marquée « Vaucluse » il
    désigne Pernes-les-Fontaines. Mieux vaut laisser Nominatim trancher que
    placer la carte à 900 km.
    """
    _charger()
    entrees = _communes.get(normaliser(nom)) or []
    code = code_departement(departement) if departement else None
    if code and entrees:
        return [e for e in entrees if e["departement"] == code]
    return entrees


def liste_departements():
    """Départements par ordre alphabétique, pour le choix proposé au visiteur."""
    _charger()
    return sorted(nom for nom in _departements.values() if nom.strip())


def code_departement(nom):
    """Code du département à partir de son nom (« Vaucluse » → « 84 »)."""
    _charger()
    return _codes_departements.get(normaliser(nom))


def coordonnees(nom, departement=None):
    """Coordonnées de la commune si le nom est sans ambiguïté, sinon None.

    Le département imprimé sur la carte sert précisément à cela : « Pernes »
    existe dans le Pas-de-Calais et « Pernes-les-Fontaines » en Vaucluse.
    """
    entrees = _entrees(nom, departement)
    if len(entrees) != 1 or entrees[0]["lat"] is None:
        return None
    entree = entrees[0]
    return {"lat": entree["lat"], "lon": entree["lon"], "adresse": entree["nom"]}


def _est_absent(valeur):
    n = normaliser(valeur)
    return not n or n.startswith("aucun")


def corriger(resultat, absents=None, departement_declare=None):
    """Remet les noms au bon niveau quand deux niveaux se contredisent.

    departement_declare : le département annoncé par le visiteur (celui de son
    service d'archives). Il ne remplace pas le département imprimé sur la carte,
    qui reste prioritaire — un fonds contient des cartes d'ailleurs — mais il
    prend le relais quand la carte n'en imprime aucun.

    Returns:
        (resultat corrigé, liste de phrases expliquant chaque correction)
    """
    absents = absents or {}
    corrige = dict(resultat or {})
    notes = []

    commune = corrige.get("commune")
    commune_absente = _est_absent(commune)
    departement = corrige.get("departement")
    departement = None if _est_absent(departement) else str(departement).strip()
    if departement and not est_departement(departement):
        # Le modèle invente parfois un libellé (« Pays d'Avignon (Vaucluse) ») :
        # ajouté aux requêtes Nominatim, il les fait toutes échouer.
        notes.append(f"« {departement} » n'est pas un département : ignoré.")
        departement = None
        corrige["departement"] = absents.get("departement", "")
    if departement is None and departement_declare:
        departement = str(departement_declare).strip()
        corrige["departement"] = departement

    # 1. La commune annoncée porte un nom de département (« Vaucluse »,
    #    « Ardèche »), ou manque : si un autre niveau nomme une commune, c'est
    #    elle la bonne. On corrige sur la contradiction entre deux niveaux, pas
    #    sur un nom isolé — « Vaucluse » est aussi une commune du Doubs.
    if commune_absente or est_departement(commune):
        for niveau in ("lieu_dit", "monument"):
            valeur = corrige.get(niveau)
            if _est_absent(valeur) or not est_commune(valeur):
                continue
            if normaliser(valeur) == normaliser(commune):
                continue
            officiel = nom_officiel(valeur, departement)
            notes.append(
                f"« {valeur} » est une commune : nous l'avons retenue comme commune "
                + (f"plutôt que « {commune} », qui est un département."
                   if not commune_absente else "alors que le modèle n'en proposait pas.")
            )
            corrige["commune"] = officiel
            corrige[niveau] = absents.get(niveau, "")
            commune = officiel
            commune_absente = False
            break

    # 2. Le même nom répété à deux niveaux : on ne le garde qu'à celui de la commune.
    if not _est_absent(commune):
        for niveau in ("lieu_dit", "monument"):
            valeur = corrige.get(niveau)
            if not _est_absent(valeur) and normaliser(valeur) == normaliser(commune):
                corrige[niveau] = absents.get(niveau, "")
                notes.append(
                    f"« {valeur} » étant le nom de la commune, il n'a pas été retenu "
                    "comme lieu plus précis."
                )

    # 3. Orthographe officielle, utile au géocodage.
    if not _est_absent(commune) and est_commune(commune):
        officiel = nom_officiel(commune, departement)
        if officiel != commune:
            corrige["commune"] = officiel

    return corrige, notes
