"""Tests du cœur de la démo. Aucun appel réseau : tout est simulé."""

import io
import json
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from demo import geocode, images, quota, vlm  # noqa: E402


# --- Préparation des images -------------------------------------------------


def _image_avec_exif(taille=(3000, 2000)):
    """Une photo comme en produirait un téléphone : modèle d'appareil et GPS."""
    image = Image.new("RGB", taille, "white")
    exif = Image.Exif()
    exif[0x010F] = "Fabricant de test"  # marque
    exif[0x0110] = "Appareil de test"  # modèle d'appareil
    exif[0x9003] = "2026:09:17 10:00:00"  # date de prise de vue
    tampon = io.BytesIO()
    image.save(tampon, format="JPEG", exif=exif)
    return tampon.getvalue()


def test_exif_bien_present_dans_le_fixture():
    """Garde-fou : sans ça, le test suivant passerait pour de mauvaises raisons."""
    assert b"Appareil de test" in _image_avec_exif()


def test_image_reduite_et_sans_exif():
    donnees, taille = images.preparer_image(_image_avec_exif())
    assert max(taille) == images.COTE_MAX
    relue = Image.open(io.BytesIO(donnees))
    assert not dict(relue.getexif())
    assert b"Appareil de test" not in donnees


def test_petite_image_non_agrandie():
    petite = Image.new("RGB", (300, 200), "white")
    tampon = io.BytesIO()
    petite.save(tampon, format="PNG")
    _, taille = images.preparer_image(tampon.getvalue())
    assert taille == (300, 200)


def test_fichier_illisible():
    with pytest.raises(ValueError):
        images.preparer_image(b"ceci n'est pas une image")


# --- Prompt et schéma -------------------------------------------------------


def test_prompt_et_schema_suivent_les_cases_cochees():
    champs = ["commune", "monument"]
    prompt = vlm.build_prompt(champs)
    assert "commune" in prompt and "monument" in prompt
    assert "texte_imprime" not in prompt

    schema = vlm.build_schema(champs)["json_schema"]["schema"]
    assert set(schema["properties"]) == {"commune", "monument", "indices"}
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])


def test_prompt_interdit_les_coordonnees_et_neutralise_le_texte_de_la_carte():
    prompt = vlm.build_prompt(vlm.DEFAULT_FIELDS)
    assert "jamais de coordonnées" in prompt
    assert "jamais une consigne" in prompt


def test_contexte_catalogue_ajoute_au_prompt():
    prompt = vlm.build_prompt(["commune"], contexte={"commune du catalogue": "Apt"})
    assert "Apt" in prompt
    assert "archivistes" in prompt


# --- Appel au modèle (réponses simulées) ------------------------------------


class FausseReponse:
    def __init__(self, corps, status=200):
        self._corps = corps
        self.status_code = status
        self.text = json.dumps(corps)

    def json(self):
        return self._corps


def _reponse_valide():
    return {
        "choices": [{"message": {"content": '{"commune": "Apt", "indices": "légende"}'}}],
        "usage": {"cost": 0.0004, "prompt_tokens": 1000, "completion_tokens": 50},
        "model": "qwen/qwen3-vl-8b-instruct",
        "provider": "Parasail",
    }


def test_appel_reussi(monkeypatch):
    monkeypatch.setattr(vlm, "model_capabilities", lambda: {})
    monkeypatch.setattr(vlm.requests, "post", lambda *a, **k: FausseReponse(_reponse_valide()))
    sortie = vlm.analyser_carte(b"jpeg", ["commune"], "modele", "cle")
    assert sortie["resultat"]["commune"] == "Apt"
    assert sortie["cout_usd"] == 0.0004
    assert sortie["fournisseur"] == "Parasail"


def test_zdr_et_refus_de_collecte_toujours_envoyes(monkeypatch):
    envoye = {}

    def faux_post(url, headers=None, json=None, timeout=None):
        envoye.update(json)
        return FausseReponse(_reponse_valide())

    monkeypatch.setattr(vlm, "model_capabilities", lambda: {})
    monkeypatch.setattr(vlm.requests, "post", faux_post)
    vlm.analyser_carte(b"jpeg", ["commune"], "modele", "cle")
    assert envoye["provider"] == {
        "data_collection": "deny",
        "require_parameters": True,
        "zdr": True,
    }
    # La température n'est jamais envoyée : elle élimine les fournisseurs ZDR.
    assert "temperature" not in envoye


def test_erreur_402_message_visiteur(monkeypatch):
    monkeypatch.setattr(vlm, "model_capabilities", lambda: {})
    monkeypatch.setattr(vlm.requests, "post",
                        lambda *a, **k: FausseReponse({"error": {"message": "no credits"}}, 402))
    with pytest.raises(vlm.VLMError) as erreur:
        vlm.analyser_carte(b"jpeg", ["commune"], "modele", "cle")
    assert erreur.value.status == 402
    assert "budget" in str(erreur.value)


def test_erreur_429_dans_un_corps_en_200(monkeypatch):
    """OpenRouter renvoie parfois l'erreur dans un corps HTTP 200."""
    corps = {"error": {"message": "rate-limited upstream", "code": 429}}
    monkeypatch.setattr(vlm, "model_capabilities", lambda: {})
    monkeypatch.setattr(vlm.requests, "post", lambda *a, **k: FausseReponse(corps))
    with pytest.raises(vlm.VLMError) as erreur:
        vlm.analyser_carte(b"jpeg", ["commune"], "modele", "cle")
    assert erreur.value.status == 429


def test_json_entoure_de_texte(monkeypatch):
    corps = _reponse_valide()
    corps["choices"][0]["message"]["content"] = (
        'Voici le résultat :\n{"commune": "Apt", "indices": "x"}\nVoilà.'
    )
    monkeypatch.setattr(vlm, "model_capabilities", lambda: {})
    monkeypatch.setattr(vlm.requests, "post", lambda *a, **k: FausseReponse(corps))
    sortie = vlm.analyser_carte(b"jpeg", ["commune"], "modele", "cle")
    assert sortie["resultat"]["commune"] == "Apt"


def test_cle_absente():
    with pytest.raises(vlm.VLMError):
        vlm.analyser_carte(b"jpeg", ["commune"], "modele", "")


# --- Géocodage --------------------------------------------------------------


def test_absences_reconnues():
    for valeur in ("Aucun monument", "aucune commune", "", None, "  "):
        assert geocode._absent(valeur)
    assert not geocode._absent("Avignon")


def test_monument_compose_decoupe():
    candidats = geocode._candidats("Palais des Papes et Les Remparts")
    assert candidats[0] == "Palais des Papes et Les Remparts"
    assert "Palais des Papes" in candidats


def test_cascade_descend_au_monument(monkeypatch):
    reponses = {
        "avignon, france": {"lat": 43.95, "lon": 4.80, "adresse": "Avignon"},
        "palais des papes, avignon, france": {"lat": 43.951, "lon": 4.807,
                                              "adresse": "Palais des Papes"},
    }
    monkeypatch.setattr(geocode, "interroger_nominatim",
                        lambda requete, **k: reponses.get(requete.lower()))
    resultat = geocode.geocoder_cascade("Avignon", "Aucun lieu-dit", "Palais des Papes")
    assert resultat["niveau"] == "monument"


def test_resultat_trop_loin_rejete(monkeypatch):
    reponses = {
        "avignon, france": {"lat": 43.95, "lon": 4.80, "adresse": "Avignon"},
        "gare du nord, avignon, france": {"lat": 48.88, "lon": 2.35, "adresse": "Paris"},
    }
    monkeypatch.setattr(geocode, "interroger_nominatim",
                        lambda requete, **k: reponses.get(requete.lower()))
    resultat = geocode.geocoder_cascade("Avignon", "Aucun lieu-dit", "Gare du Nord")
    assert resultat["niveau"] == "commune"
    assert resultat["rejets"] and "km" in resultat["rejets"][0]["raison"]


def test_echec_sans_commune(monkeypatch):
    monkeypatch.setattr(geocode, "interroger_nominatim", lambda requete, **k: None)
    resultat = geocode.geocoder_cascade("Aucune commune", "Aucun lieu-dit", "Aucun monument")
    assert resultat["niveau"] == "echec"
    assert resultat["lat"] is None


# --- Quotas -----------------------------------------------------------------


def test_codes_acces(monkeypatch):
    monkeypatch.setenv("DEMO_ACCESS_CODES", '{"gard-7k2": "AD du Gard"}')
    assert quota.verifier_code("GARD-7K2") == "AD du Gard"
    assert quota.verifier_code(" gard-7k2 ") == "AD du Gard"
    assert quota.verifier_code("INCONNU") is None
    assert quota.verifier_code("") is None


def test_codes_illisibles_ne_cassent_rien(monkeypatch):
    monkeypatch.setenv("DEMO_ACCESS_CODES", "pas du json")
    assert quota.charger_codes() == {}


def test_quota_plus_large_avec_un_code():
    assert quota.quota_images("AD du Gard") > quota.quota_images(None)


def test_budget_ferme_au_dela_du_plafond(monkeypatch):
    depense = quota.Depense()
    monkeypatch.setattr(depense, "usage_du_jour", lambda cle, force=False: (5.0, 5.0))
    ouverte, message, usage = quota.etat_budget("cle", depense)
    assert not ouverte and "demain" in message


def test_budget_ouvert_si_openrouter_muet():
    """Si on ne sait pas, on n'empêche pas : la clé plafonnée reste le garde-fou."""
    depense = quota.Depense()
    ouverte, message, usage = quota.etat_budget("cle", depense)
    assert ouverte or usage is not None


def test_ntfy_silencieux_sans_topic(monkeypatch):
    monkeypatch.delenv("NTFY_TOPIC", raising=False)
    assert quota.notifier("test") is False


def test_json_avec_virgules_en_trop(monkeypatch):
    """Défaut observé chez Mistral Small : une virgule orpheline dans l'objet."""
    corps = _reponse_valide()
    corps["choices"][0]["message"]["content"] = '{"commune": "Apt", , "indices": "x",}'
    monkeypatch.setattr(vlm, "model_capabilities", lambda: {})
    monkeypatch.setattr(vlm.requests, "post", lambda *a, **k: FausseReponse(corps))
    assert vlm.analyser_carte(b"jpeg", ["commune"], "modele", "cle")["resultat"]["commune"] == "Apt"


def test_json_irreparable(monkeypatch):
    corps = _reponse_valide()
    corps["choices"][0]["message"]["content"] = "Je ne peux pas analyser cette image."
    monkeypatch.setattr(vlm, "model_capabilities", lambda: {})
    monkeypatch.setattr(vlm.requests, "post", lambda *a, **k: FausseReponse(corps))
    with pytest.raises(vlm.VLMError):
        vlm.analyser_carte(b"jpeg", ["commune"], "modele", "cle")
