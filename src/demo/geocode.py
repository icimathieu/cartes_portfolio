"""
Géocodage en cascade via Nominatim, sans base de connaissances externe.

Reprise de la logique de `cartes_workshop/lib/nominatim.py`, privée de la
validation croisée avec les métadonnées du fonds (la démo n'en a pas) :

  1. monument + commune
  2. lieu-dit + commune
  3. commune seule

Un résultat situé à plus de FILTRE_KM du centre de la commune est rejeté :
c'est le garde-fou contre les homonymes d'un bout à l'autre de la France.

Politique d'usage Nominatim : une requête par seconde au maximum pour toute
l'application, un User-Agent identifiable, et attribution OpenStreetMap
affichée à côté du résultat.
"""

import math
import re
import threading
import time

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = (
    "cartes-postales-demo/1.0 (CartaData, École nationale des chartes - PSL; "
    "mathieu.riviere@chartes.psl.eu)"
)
ATTRIBUTION = "© Contributeurs OpenStreetMap — géocodage Nominatim"
DELAI_ENTRE_APPELS = 1.1
FILTRE_KM = 20.0

NIVEAUX = {
    "monument": "monument ou édifice",
    "lieu_dit": "lieu-dit ou quartier",
    "commune": "commune",
    "departement": "département",
    "echec": "aucun lieu trouvé",
}

_verrou = threading.Lock()
_dernier_appel = [0.0]
_cache = {}


def _absent(valeur):
    if not valeur or not str(valeur).strip():
        return True
    return str(valeur).strip().lower().startswith("aucun")


def _candidats(valeur):
    """Termes à essayer pour un même niveau, du plus complet au plus simple.

    Les modèles renvoient souvent plusieurs lieux d'un coup (« Palais des Papes et
    les Remparts »), introuvables tels quels dans OpenStreetMap : on retente alors
    chaque partie séparément.
    """
    terme = str(valeur).strip()
    essais = [terme]
    for separateur in (" et ", " & ", ", "):
        if separateur in terme.lower():
            morceaux = re.split(separateur, terme, flags=re.IGNORECASE)
            essais += [m.strip() for m in morceaux if len(m.strip()) > 3]
            break
    vus, propres = set(), []
    for essai in essais:
        cle = essai.lower()
        if essai and cle not in vus:
            vus.add(cle)
            propres.append(essai)
    return propres


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def interroger_nominatim(requete, timeout=15):
    """Un appel Nominatim, mis en cache et limité à une requête par seconde."""
    if not requete or not requete.strip():
        return None
    cle = requete.strip().lower()
    if cle in _cache:
        return _cache[cle]

    with _verrou:
        attente = DELAI_ENTRE_APPELS - (time.monotonic() - _dernier_appel[0])
        if attente > 0:
            time.sleep(attente)
        try:
            resp = requests.get(
                NOMINATIM_URL,
                params={
                    "q": requete,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                    "countrycodes": "fr",
                },
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
            )
            donnees = resp.json() if resp.status_code == 200 else []
        except (requests.RequestException, ValueError):
            donnees = []
        finally:
            _dernier_appel[0] = time.monotonic()

    resultat = None
    if donnees:
        resultat = {
            "lat": float(donnees[0]["lat"]),
            "lon": float(donnees[0]["lon"]),
            "adresse": donnees[0].get("display_name", ""),
        }
    _cache[cle] = resultat
    return resultat


def geocoder_cascade(commune=None, lieu_dit=None, monument=None, ancre=None,
                     departement=None):
    """Géocode le lieu le plus précis possible.

    ancre : coordonnées de la commune déjà connues (référentiel officiel). Elles
    évitent un appel à Nominatim et, surtout, une commune homonyme à l'autre
    bout de la France.

    Returns:
        dict : niveau, libelle_niveau, lat, lon, adresse, requete, distance_commune_km,
        rejets (liste des requêtes écartées et pourquoi). Le niveau vaut "echec"
        si rien n'a pu être géocodé.
    """
    rejets = []
    commune_propre = None if _absent(commune) else str(commune).strip()
    dept = None if _absent(departement) else str(departement).strip()
    # Le département imprimé sur la carte lève les homonymes de communes.
    suffixe = f", {dept}, France" if dept else ", France"

    if ancre is None and commune_propre:
        ancre = interroger_nominatim(f"{commune_propre}{suffixe}")

    for niveau, valeur in (("monument", monument), ("lieu_dit", lieu_dit)):
        if _absent(valeur) or not commune_propre:
            continue
        for terme in _candidats(valeur):
            requete = f"{terme}, {commune_propre}{suffixe}"
            trouve = interroger_nominatim(requete)
            if not trouve:
                rejets.append({"requete": requete, "raison": "introuvable dans OpenStreetMap"})
                continue
            distance = None
            if ancre:
                distance = haversine_km(trouve["lat"], trouve["lon"], ancre["lat"], ancre["lon"])
                if distance > FILTRE_KM:
                    rejets.append({
                        "requete": requete,
                        "raison": f"écarté : à {distance:.0f} km de {commune_propre}",
                    })
                    continue
            return {
                "niveau": niveau,
                "libelle_niveau": NIVEAUX[niveau],
                "lat": trouve["lat"],
                "lon": trouve["lon"],
                "adresse": trouve["adresse"],
                "requete": requete,
                "distance_commune_km": None if distance is None else round(distance, 1),
                "rejets": rejets,
            }

    if ancre:
        return {
            "niveau": "commune",
            "libelle_niveau": NIVEAUX["commune"],
            "lat": ancre["lat"],
            "lon": ancre["lon"],
            "adresse": ancre["adresse"],
            "requete": f"{commune_propre}{suffixe}",
            "distance_commune_km": 0.0,
            "rejets": rejets,
        }

    # Dernier recours : la carte nomme un département mais aucune commune
    # identifiable. Mieux vaut un point à cette échelle qu'aucun point.
    if dept:
        trouve = interroger_nominatim(f"{dept}, France")
        if trouve:
            return {
                "niveau": "departement",
                "libelle_niveau": NIVEAUX["departement"],
                "lat": trouve["lat"],
                "lon": trouve["lon"],
                "adresse": trouve["adresse"],
                "requete": f"{dept}, France",
                "distance_commune_km": None,
                "rejets": rejets,
            }

    return {
        "niveau": "echec",
        "libelle_niveau": NIVEAUX["echec"],
        "lat": None,
        "lon": None,
        "adresse": None,
        "requete": None,
        "distance_commune_km": None,
        "rejets": rejets,
    }
