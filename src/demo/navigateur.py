"""
Détection du navigateur, pour un seul usage : prévenir du téléversement refusé.

Le Space est aussi consulté depuis la page huggingface.co, qui l'affiche dans
un cadre servi par un autre domaine. Le cookie anti-CSRF de Streamlit y est un
cookie tiers : Firefox et Chrome le cloisonnent mais l'acceptent, Safari le
refuse. Sans lui, le téléversement échoue par une erreur 403 que Streamlit
affiche sans l'expliquer, et que notre code ne peut pas intercepter — elle se
produit dans le navigateur, avant d'arriver jusqu'à nous. D'où cet avertissement
affiché d'avance aux seuls navigateurs concernés.
"""

# Tous les navigateurs d'iOS sont des WebKit déguisés : la règle de Safari
# s'applique à eux aussi, quel que soit le nom affiché.
_MARQUEURS_IOS = ("CriOS", "FxiOS", "EdgiOS", "iPhone", "iPad", "iPod")
# Ces navigateurs mettent « Safari » dans leur signature sans en être.
_FAUX_SAFARI = ("Chrome", "Chromium", "Edg/", "OPR/", "Brave", "SamsungBrowser")


def refuse_les_cookies_tiers(user_agent):
    """Vrai si ce navigateur bloque les cookies d'un cadre venu d'un autre site."""
    ua = str(user_agent or "")
    if any(marqueur in ua for marqueur in _MARQUEURS_IOS):
        return True
    return "Safari" in ua and not any(faux in ua for faux in _FAUX_SAFARI)
