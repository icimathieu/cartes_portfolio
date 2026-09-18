"""
Vérification des noms de lieux contre le référentiel officiel des communes.

Le visiteur indique le département de son service d'archives. Cette indication
n'est pas décorative : elle réduit le référentiel aux seules communes de ce
département, et c'est cette liste courte qui sert à corriger le modèle.

Trois choses en découlent :

  - **Un nom de commune ne peut aller que dans le champ commune.** Sur une carte
    de « FONTAINE DE VAUCLUSE — La Place », le modèle a répondu commune
    « Vaucluse », monument « Fontaine de Vaucluse ». Comme Fontaine-de-Vaucluse
    est une commune du département retenu et que « Vaucluse » n'en est pas une,
    les deux niveaux sont remis à leur place.
  - **Les homonymes sont levés et les noms d'époque traduits.** « Pernes »
    existe dans le Pas-de-Calais ; dans le Vaucluse, c'est le nom que portait
    Pernes-les-Fontaines quand la carte a été imprimée. Restreindre au
    département donne une réponse unique, donc des coordonnées exactes sans
    passer par Nominatim (voir `resoudre`).
  - **Les départements inventés disparaissent.** « Pays d'Avignon (Vaucluse) »
    n'est pas un département : le département déclaré prend sa place.

Le département déclaré l'emporte sur celui que le modèle croit lire sur la
carte : le premier est saisi par un archiviste, le second est une lecture
d'image. Quand les deux divergent, la carte vient probablement d'un autre
fonds ; on le signale et on rend sa liberté au géocodage plutôt que de forcer
un département qui ferait échouer toutes les requêtes.

La vérification ne peut jamais être naïve : « Vaucluse » est à la fois un
département et une commune du Doubs. On ne corrige donc que sur une
contradiction, jamais sur un nom isolé — une règle qui écartait la commune dès
qu'elle portait le nom du département a été retirée après mesure : elle perdait
deux cartes sur le jeu de référence et n'en gagnait aucune.

Le référentiel vient des communes de France (INSEE / La Poste, données
ouvertes), réduit à ce qui sert ici : nom, département, coordonnées.
"""

import csv
import difflib
import re
import unicodedata
from pathlib import Path

# Chemin calculé depuis ce fichier et non depuis le dossier courant : sans quoi
# le référentiel est introuvable dès que l'application est lancée d'ailleurs
# (le banc d'essai l'a été, et mesurait une chaîne sans aucune vérification).
RACINE_ASSETS = Path(__file__).resolve().parents[2] / "assets" / "referentiel"
FICHIER_COMMUNES = "communes_france.csv"
FICHIER_DEPARTEMENTS = "departements_france.csv"

_communes = None
_departements = None
_codes_departements = None
_noms_par_code = None
_par_departement = None


def normaliser(valeur):
    """« Fontaine-de-Vaucluse » et « FONTAINE DE VAUCLUSE » donnent la même clé."""
    if not valeur:
        return ""
    texte = unicodedata.normalize("NFKD", str(valeur)).encode("ascii", "ignore").decode()
    texte = texte.lower()
    return " ".join("".join(c if c.isalnum() else " " for c in texte).split())


def _charger():
    global _communes, _departements, _codes_departements, _noms_par_code, _par_departement
    if _communes is not None:
        return
    _communes, _departements, _codes_departements = {}, {}, {}
    _noms_par_code, _par_departement = {}, {}
    chemin = RACINE_ASSETS / FICHIER_COMMUNES
    if chemin.exists():
        with chemin.open(encoding="utf-8") as flux:
            for ligne in csv.DictReader(flux):
                entree = {
                    "nom": ligne["nom"],
                    "cle": ligne["cle"],
                    "departement": ligne["departement"],
                    "lat": float(ligne["latitude"]) if ligne["latitude"] else None,
                    "lon": float(ligne["longitude"]) if ligne["longitude"] else None,
                }
                _communes.setdefault(ligne["cle"], []).append(entree)
                _par_departement.setdefault(ligne["departement"], []).append(entree)
    chemin = RACINE_ASSETS / FICHIER_DEPARTEMENTS
    if chemin.exists():
        with chemin.open(encoding="utf-8") as flux:
            for ligne in csv.DictReader(flux):
                if not ligne["nom"].strip():
                    continue
                _departements[ligne["cle"]] = ligne["nom"]
                _codes_departements[ligne["cle"]] = ligne.get("code", "")
                _noms_par_code[ligne.get("code", "")] = ligne["nom"]


def est_commune(nom):
    _charger()
    return normaliser(nom) in _communes


def est_departement(nom):
    _charger()
    return normaliser(nom) in _departements


def liste_departements():
    """Départements par ordre alphabétique, pour le choix proposé au visiteur."""
    _charger()
    return sorted(_departements.values())


def code_departement(nom):
    """Code du département à partir de son nom (« Vaucluse » → « 84 »)."""
    _charger()
    return _codes_departements.get(normaliser(nom))


def nom_departement(nom):
    """Orthographe officielle du département, ou le nom d'origine."""
    _charger()
    return _departements.get(normaliser(nom), nom)


def communes_du_departement(departement):
    """Toutes les communes d'un département — la liste courte qui sert à corriger."""
    _charger()
    code = code_departement(departement)
    return _par_departement.get(code, []) if code else []


ABREVIATIONS = {"st": "saint", "ste": "sainte", "sts": "saints", "stes": "saintes",
                "mt": "mont", "nd": "notre dame"}


def _formes(nom):
    """Écritures équivalentes d'un même nom de commune.

    Les légendes et les catalogues abrègent (« St-Pantaléon ») et inversent
    l'article (« Thor (Le) », « Isle-sur-la-Sorgue (L') ») ; le référentiel,
    lui, écrit « Saint-Pantaléon » et « Le Thor ».
    """
    cle = normaliser(nom)
    formes = [cle]
    developpee = " ".join(ABREVIATIONS.get(mot, mot) for mot in cle.split())
    if developpee != cle:
        formes.append(developpee)
    for forme in list(formes):
        article = re.match(r"^(.*?)\s+(le|la|les|l)$", forme)
        if article:
            formes.append(f"{article.group(2)} {article.group(1)}")
    return formes


def resoudre(nom, departement=None):
    """L'entrée officielle de la commune portant ce nom, ou None si indécidable.

    Le modèle lit le nom **tel qu'il était imprimé**, et une carte postale
    ancienne est antérieure à la plupart des renommages : Vaison est devenue
    Vaison-la-Romaine en 1924, Pernes s'est faite Pernes-les-Fontaines, Saumane
    a gagné son « de-Vaucluse ». Le référentiel, lui, ne connaît que les noms
    d'aujourd'hui. Rapprocher les deux n'est donc pas une tolérance à la
    négligence : c'est la traduction d'un nom d'époque en nom actuel.

    Restreint à un département, le rapprochement est sûr parce qu'un seul nom
    peut correspondre. Sont acceptés : le nom d'avant le déterminant
    (« Pernes »), le nom rallongé par la légende (« Mérindol-le-Vieux »),
    l'abréviation (« St-Pantaléon »), l'article inversé des catalogues
    (« Thor (Le) ») et une variation d'une lettre (« Saumanes »).
    """
    _charger()
    if not normaliser(nom):
        return None

    for cle in _formes(nom):
        entrees = _communes.get(cle) or []
        if not departement:
            if len(entrees) == 1:
                return entrees[0]
            continue

        code = code_departement(departement)
        if code is None:
            return None
        dans_le_departement = [e for e in entrees if e["departement"] == code]
        if dans_le_departement:
            return dans_le_departement[0]

        voisines = _par_departement.get(code, [])
        # Nom d'avant le renommage (« Pernes » pour Pernes-les-Fontaines) ou
        # rallongé par la légende (« Mérindol-le-Vieux ») : accepté tant qu'une
        # seule commune du département peut correspondre.
        # Le sens « nom rallongé » ne vaut que si ce nom n'est pas lui-même une
        # commune ailleurs : « Sault-de-Navailles » existe dans les
        # Pyrénées-Atlantiques et ne doit pas devenir Sault, en Vaucluse.
        rallonge = not entrees
        prefixes = [e for e in voisines
                    if e["cle"].startswith(cle + " ")
                    or (rallonge and cle.startswith(e["cle"] + " "))]
        if len(prefixes) == 1:
            return prefixes[0]
        # Variation d'une lettre, sur le nom entier ou sur sa tête
        # (« Saumanes » pour Saumane-de-Vaucluse) : les graphies anciennes
        # flottent. Accepté seulement si une seule commune du département ressort.
        index = {}
        for e in voisines:
            index.setdefault(e["cle"], []).append(e)
            tete = e["cle"].split(" ")[0]
            if tete != e["cle"]:
                index.setdefault(tete, []).append(e)
        proches = difflib.get_close_matches(cle, list(index), n=3, cutoff=0.9)
        candidats = {e["cle"]: e for texte in proches for e in index[texte]}
        if len(candidats) == 1:
            return next(iter(candidats.values()))

    return None


def nom_officiel(nom, departement=None):
    """Orthographe officielle de la commune, ou le nom d'origine."""
    entree = resoudre(nom, departement)
    return entree["nom"] if entree else nom


def coordonnees(nom, departement=None):
    """Coordonnées de la commune si le nom est sans ambiguïté, sinon None."""
    entree = resoudre(nom, departement)
    if entree is None or entree["lat"] is None:
        return None
    return {"lat": entree["lat"], "lon": entree["lon"], "adresse": entree["nom"]}


def _est_absent(valeur):
    n = normaliser(valeur)
    return not n or n.startswith("aucun")


def departement_du_code(code):
    """« 84 » → « Vaucluse »."""
    _charger()
    return _noms_par_code.get(str(code))


def _departement_retenu(corrige, departement_declare, notes):
    """Quel département sert de cadre à l'analyse.

    Le département déclaré par le service d'archives l'emporte : il est saisi
    par un archiviste qui connaît son fonds, là où celui du modèle est une
    lecture d'image, parfois inventée. Si la carte en imprime un autre, la
    commune tranchera plus bas — c'est elle, et non le modèle, qui décide.
    """
    imprime = corrige.get("departement")
    imprime = None if _est_absent(imprime) else str(imprime).strip()
    if imprime and not est_departement(imprime):
        # Le modèle invente parfois un libellé (« Pays d'Avignon (Vaucluse) ») :
        # ajouté aux requêtes Nominatim, il les fait toutes échouer.
        if not departement_declare:
            notes.append(f"« {imprime} » n'est pas un département : ignoré.")
        imprime = None

    if not departement_declare:
        return (nom_departement(imprime) if imprime else None), imprime
    return nom_departement(departement_declare), imprime


def corriger(resultat, absents=None, departement_declare=None):
    """Remet les noms au bon niveau à partir des communes du département retenu.

    departement_declare : le département du service d'archives, tel qu'indiqué
    par le visiteur. Il fait foi, sauf si la carte en imprime un autre.

    Returns:
        (resultat corrigé, liste de phrases expliquant chaque correction)
    """
    absents = absents or {}
    corrige = dict(resultat or {})
    notes = []

    departement, imprime = _departement_retenu(corrige, departement_declare, notes)
    if departement or "departement" in corrige:
        corrige["departement"] = departement or absents.get("departement", "")

    # 1. La commune annoncée doit être une commune du département retenu. Sinon
    #    — elle manque, elle porte un nom de département (« Vaucluse »), ou elle
    #    est d'ailleurs — un nom de commune trouvé à un autre niveau prend sa
    #    place : un nom de commune n'a rien à faire ailleurs que dans ce champ.
    commune = corrige.get("commune")
    commune_absente = _est_absent(commune)
    entree = None if commune_absente else resoudre(commune, departement)

    if entree is None or est_departement(commune):
        for niveau in ("lieu_dit", "monument"):
            valeur = corrige.get(niveau)
            if _est_absent(valeur) or normaliser(valeur) == normaliser(commune):
                continue
            autre = resoudre(valeur, departement)
            if autre is None:
                continue
            if commune_absente:
                raison = "alors que le modèle n'en proposait pas."
            elif est_departement(commune):
                raison = f"plutôt que « {commune} », qui est un département."
            else:
                raison = f"plutôt que « {commune} », inconnue dans ce département."
            notes.append(f"« {valeur} » est une commune : nous l'avons retenue comme commune " + raison)
            corrige["commune"] = autre["nom"]
            corrige[niveau] = absents.get(niveau, "")
            commune, commune_absente, entree = autre["nom"], False, autre
            break

    # 2. La commune existe, mais pas dans le département déclaré : un fonds
    #    départemental contient aussi des cartes d'ailleurs. C'est la commune
    #    qui tranche, pas le département annoncé — on suit celui où elle se
    #    trouve vraiment, et à défaut on rend sa liberté au géocodage.
    if entree is None and not commune_absente and departement and est_commune(commune):
        homonymes = _communes[normaliser(commune)]
        ailleurs = resoudre(commune, imprime) if imprime else None
        if ailleurs is None and len(homonymes) == 1:
            ailleurs = homonymes[0]
        if ailleurs is not None:
            reel = departement_du_code(ailleurs["departement"])
            notes.append(
                f"« {commune} » est une commune du département « {reel} » et non de "
                f"« {departement} » : c'est elle qui a été suivie."
            )
            corrige["departement"] = reel
            departement, entree = reel, ailleurs
        else:
            notes.append(
                f"« {commune} » n'est pas une commune du département « {departement} » "
                "et plusieurs communes portent ce nom : la recherche a été élargie à "
                "toute la France."
            )
            corrige["departement"] = absents.get("departement", "")
            departement = None

    # 3. Le même nom répété à deux niveaux : on ne le garde qu'à celui de la commune.
    if not commune_absente:
        for niveau in ("lieu_dit", "monument"):
            valeur = corrige.get(niveau)
            if not _est_absent(valeur) and normaliser(valeur) == normaliser(commune):
                corrige[niveau] = absents.get(niveau, "")
                notes.append(
                    f"« {valeur} » étant le nom de la commune, il n'a pas été retenu "
                    "comme lieu plus précis."
                )

    # 4. Orthographe officielle, utile au géocodage (« Pernes » →
    #    « Pernes-les-Fontaines » quand le département ne laisse qu'un candidat).
    if entree is not None and entree["nom"] != commune:
        notes.append(
            f"« {commune} », tel qu'imprimé sur la carte, désigne la commune aujourd'hui "
            f"appelée « {entree['nom']} »."
        )
        corrige["commune"] = entree["nom"]

    return corrige, notes
