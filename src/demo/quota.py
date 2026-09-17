"""
Garde-fous de la démo, du plus dur au plus souple.

1. Plafond absolu : la clé OpenRouter de la démo a sa propre limite en dollars,
   remise à zéro chaque nuit. Rien dans ce fichier ne peut la contourner.
2. Plafond journalier : on lit `usage_daily` de la clé auprès d'OpenRouter et on
   refuse les essais au-delà du seuil. Cette valeur vit chez OpenRouter, donc
   elle survit à un redémarrage du Space sans que nous stockions quoi que ce soit.
3. Quota par visiteur : un nombre d'images par session, plus généreux avec un
   code d'accès personnel envoyé dans nos mails de prospection.

Le compteur par session repart à zéro si le visiteur recharge la page : c'est
assumé, puisque les plafonds 1 et 2 bornent la dépense. On ne demande ni compte,
ni adresse mail, et on ne stocke aucune donnée du visiteur.
"""

import json
import os
import threading
import time

import requests

KEY_URL = "https://openrouter.ai/api/v1/key"

IMAGES_ANONYME = int(os.environ.get("DEMO_IMAGES_ANONYME", "10"))
IMAGES_AVEC_CODE = int(os.environ.get("DEMO_IMAGES_AVEC_CODE", "30"))
PLAFOND_JOURNALIER_USD = float(os.environ.get("DEMO_PLAFOND_JOUR_USD", "1.0"))
DUREE_CACHE_USAGE = 60  # secondes


class Depense:
    """Cache du coût du jour, partagé par toutes les sessions du Space."""

    def __init__(self):
        self._verrou = threading.Lock()
        self._instant = 0.0
        self._usage = None
        self._limite_cle = None

    def usage_du_jour(self, api_key, force=False):
        """(usage_usd, limite_cle_usd) ou (None, None) si OpenRouter est muet."""
        with self._verrou:
            frais = time.monotonic() - self._instant < DUREE_CACHE_USAGE
            if frais and not force:
                return self._usage, self._limite_cle
            try:
                resp = requests.get(
                    KEY_URL,
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10,
                )
                donnees = resp.json()["data"]
                self._usage = float(donnees.get("usage_daily") or 0.0)
                limite = donnees.get("limit")
                self._limite_cle = None if limite is None else float(limite)
                self._instant = time.monotonic()
            except Exception:
                # En cas de doute on ne bloque pas la démo : la clé plafonnée
                # reste le garde-fou qui ne peut pas échouer.
                pass
            return self._usage, self._limite_cle

    def ajouter(self, cout):
        """Incrémente l'estimation locale entre deux lectures chez OpenRouter."""
        with self._verrou:
            if cout and self._usage is not None:
                self._usage += cout


def charger_codes():
    """Codes d'accès, lus depuis le secret DEMO_ACCESS_CODES.

    Format attendu : {"GARD-7K2": "AD du Gard", ...}. Les libellés ne sont
    affichés à personne, ils servent uniquement à la notification ntfy.
    """
    brut = os.environ.get("DEMO_ACCESS_CODES", "").strip()
    if not brut:
        return {}
    try:
        codes = json.loads(brut)
    except ValueError:
        return {}
    return {str(k).strip().upper(): str(v) for k, v in codes.items()}


def verifier_code(saisie):
    """Retourne le libellé associé au code, ou None."""
    if not saisie:
        return None
    return charger_codes().get(saisie.strip().upper())


def quota_images(libelle_code=None):
    return IMAGES_AVEC_CODE if libelle_code else IMAGES_ANONYME


def etat_budget(api_key, depense):
    """Dit si la démo peut encore tourner aujourd'hui.

    Returns:
        (ouverte: bool, message: str|None, usage: float|None)
    """
    usage, limite_cle = depense.usage_du_jour(api_key)
    if usage is None:
        return True, None, None
    plafond = PLAFOND_JOURNALIER_USD
    if limite_cle is not None:
        plafond = min(plafond, limite_cle)
    if usage >= plafond:
        return False, (
            "La démo a atteint son budget du jour. Elle réouvre demain, et nous "
            "pouvons organiser un essai sur votre propre fonds quand vous voulez."
        ), usage
    return True, None, usage


def notifier(message, titre="Démo cartes postales"):
    """Notification ntfy, silencieuse en cas d'échec. Topic = secret du Space."""
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        return False
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={"Title": titre, "Tags": "postcard"},
            timeout=5,
        )
        return True
    except requests.RequestException:
        return False
