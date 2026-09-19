"""Tests du cœur de la démo. Aucun appel réseau : tout est simulé."""

import io
import json
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from demo import geocode, images, navigateur, quota, vlm  # noqa: E402


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


def test_commune_imposee_dans_le_schema():
    """La liste fermée est une contrainte de décodage, pas une consigne."""
    schema = vlm.build_schema(["commune", "monument"], ["Avignon", "Apt", "avignon"])
    commune = schema["json_schema"]["schema"]["properties"]["commune"]
    assert commune["enum"] == ["Avignon", "Apt", "Aucune commune"]
    assert "enum" not in schema["json_schema"]["schema"]["properties"]["monument"]
    # Sans liste, le modèle répond librement.
    assert "enum" not in vlm.build_schema(["commune"])["json_schema"]["schema"][
        "properties"]["commune"]


# --- Référentiel des communes -----------------------------------------------

from demo import lieux  # noqa: E402

ABSENTS = {cle: spec["absent"] for cle, spec in vlm.FIELDS.items()}


def test_departement_pris_pour_une_commune():
    """Cas réel : « FONTAINE DE VAUCLUSE — La Place » lue comme commune Vaucluse."""
    corrige, notes = lieux.corriger(
        {"commune": "Vaucluse", "lieu_dit": "La Place", "monument": "Fontaine de Vaucluse"},
        ABSENTS,
    )
    assert corrige["commune"] == "Fontaine-de-Vaucluse"
    assert corrige["monument"] == "Aucun monument"
    assert corrige["lieu_dit"] == "La Place"
    assert notes and "département" in notes[0]


def test_commune_absente_recuperee_ailleurs():
    corrige, notes = lieux.corriger(
        {"commune": "Aucune commune", "lieu_dit": "Aucun lieu-dit", "monument": "Le Thor"},
        ABSENTS,
    )
    assert corrige["commune"] == "Le Thor"
    assert notes


def test_nom_de_commune_repete_en_monument():
    corrige, _ = lieux.corriger(
        {"commune": "Fontaine-de-Vaucluse", "lieu_dit": "Aucun lieu-dit",
         "monument": "Fontaine de Vaucluse"},
        ABSENTS,
    )
    assert corrige["monument"] == "Aucun monument"


def test_resultat_correct_non_modifie():
    """Le cas nominal ne doit jamais être touché."""
    entree = {"commune": "Avignon", "lieu_dit": "Aucun lieu-dit",
              "monument": "Palais des Papes"}
    corrige, notes = lieux.corriger(dict(entree), ABSENTS)
    assert corrige == entree and notes == []


def test_pas_de_correction_sur_un_nom_isole():
    """« Vaucluse » est aussi une commune du Doubs : sans contradiction, on n'y touche pas."""
    corrige, notes = lieux.corriger(
        {"commune": "Vaucluse", "lieu_dit": "Aucun lieu-dit", "monument": "Aucun monument"},
        ABSENTS,
    )
    assert corrige["commune"] == "Vaucluse" and notes == []


def test_orthographe_officielle():
    corrige, _ = lieux.corriger({"commune": "AVIGNON"}, ABSENTS)
    assert corrige["commune"] == "Avignon"


def test_coordonnees_seulement_si_sans_ambiguite():
    assert lieux.coordonnees("fontaine de vaucluse")["lat"] == pytest.approx(43.92, abs=0.05)
    assert lieux.coordonnees("Sainte-Colombe") is None  # plusieurs communes homonymes
    assert lieux.coordonnees("Commune Qui N'Existe Pas") is None


def test_departement_leve_les_homonymes():
    """« Pernes » est dans le Pas-de-Calais ; en Vaucluse, c'est Pernes-les-Fontaines."""
    assert lieux.coordonnees("Pernes")["lat"] == pytest.approx(50.5, abs=0.3)
    assert lieux.coordonnees("Pernes", "Vaucluse")["lat"] == pytest.approx(43.99, abs=0.1)
    assert lieux.code_departement("Vaucluse") == "84"


def test_nom_abrege_complete_dans_le_departement():
    """Restreint à un département, un nom tronqué redevient identifiable."""
    assert lieux.resoudre("Pernes", "Vaucluse")["nom"] == "Pernes-les-Fontaines"
    assert lieux.resoudre("Pernes")["nom"] == "Pernes"  # unique en France sous ce nom
    corrige, notes = lieux.corriger({"commune": "Pernes"}, ABSENTS, "Vaucluse")
    assert corrige["commune"] == "Pernes-les-Fontaines"
    assert notes


def test_noms_d_epoque_traduits():
    """Une carte ancienne imprime le nom d'avant le renommage de la commune."""
    traductions = {
        "Vaison": "Vaison-la-Romaine",        # renommée en 1924
        "Pernes": "Pernes-les-Fontaines",
        "Beaumes": "Beaumes-de-Venise",
        "Saumanes": "Saumane-de-Vaucluse",    # graphie ancienne flottante
        "Mérindol-le-Vieux": "Mérindol",      # le village d'avant 1545
        "St-Pantaléon": "Saint-Pantaléon",    # abréviation de légende
        "Thor (Le)": "Le Thor",               # article inversé des catalogues
    }
    for lu, actuel in traductions.items():
        assert lieux.resoudre(lu, "Vaucluse")["nom"] == actuel, lu


def test_aucune_traduction_abusive():
    """La tolérance ne doit jamais happer une commune qui existe ailleurs."""
    for nom in ("Nîmes", "Arles", "Marseille", "Carcassonne", "Sault-de-Navailles",
                "Vaucluse", "Mont Ventoux", "Sauvans"):
        assert lieux.resoudre(nom, "Vaucluse") is None, nom


def test_lieu_sans_commune_place_dans_le_departement(monkeypatch):
    """Les cartes du mont Ventoux ne relèvent d'aucune commune."""
    monkeypatch.setattr(geocode, "interroger_nominatim",
                        lambda requete, **k: {"lat": 44.17, "lon": 5.28, "adresse": requete})
    resultat = geocode.geocoder_cascade("Aucune commune", "Mont Ventoux", "L'Observatoire",
                                        departement="Vaucluse")
    assert resultat["niveau"] == "monument"
    assert resultat["requete"] == "L'Observatoire, Vaucluse, France"


def test_commune_hors_du_departement_declare():
    """Un fonds départemental contient aussi des cartes d'ailleurs."""
    corrige, notes = lieux.corriger(
        {"commune": "Nîmes", "departement": "Aucun département"}, ABSENTS, "Vaucluse")
    assert corrige["commune"] == "Nîmes" and corrige["departement"] == "Gard"
    assert notes and "Gard" in notes[0]


def test_commune_du_departement_recuperee_dans_le_monument():
    """Le département déclaré permet de voir qu'un nom de commune est mal placé."""
    corrige, notes = lieux.corriger(
        {"commune": "Aucune commune", "lieu_dit": "Aucun lieu-dit",
         "monument": "L'Isle-sur-la-Sorgue"},
        ABSENTS, "Vaucluse")
    assert corrige["commune"] == "L'Isle-sur-la-Sorgue"
    assert corrige["monument"] == "Aucun monument"


def test_departement_invente_ignore():
    """Vu en vrai : « Pays d'Avignon (Vaucluse) », qui faisait échouer tout le géocodage."""
    corrige, notes = lieux.corriger(
        {"commune": "Avignon", "departement": "Pays d'Avignon (Vaucluse)"}, ABSENTS)
    assert corrige["departement"] == "Aucun département"
    assert corrige["commune"] == "Avignon"
    assert notes and "pas un département" in notes[0]


def test_commune_homonyme_du_departement_conservee():
    """Sans contradiction, on ne touche pas : « Vaucluse » est une commune du Doubs."""
    corrige, notes = lieux.corriger(
        {"commune": "Vaucluse", "departement": "Vaucluse",
         "lieu_dit": "Aucun lieu-dit", "monument": "Aucun monument"},
        ABSENTS,
    )
    assert corrige["commune"] == "Vaucluse"


def test_cascade_se_replie_sur_le_departement(monkeypatch):
    reponses = {"vaucluse, france": {"lat": 44.0, "lon": 5.2, "adresse": "Vaucluse"}}
    monkeypatch.setattr(geocode, "interroger_nominatim",
                        lambda requete, **k: reponses.get(requete.lower()))
    resultat = geocode.geocoder_cascade("Aucune commune", "Aucun lieu-dit",
                                        "Aucun monument", departement="Vaucluse")
    assert resultat["niveau"] == "departement"


def test_departement_present_dans_les_requetes(monkeypatch):
    vues = []

    def faux(requete, **k):
        vues.append(requete)
        return {"lat": 43.9, "lon": 4.8, "adresse": requete}

    monkeypatch.setattr(geocode, "interroger_nominatim", faux)
    geocode.geocoder_cascade("Pernes", "Aucun lieu-dit", "Porte Saint-Gilles",
                             departement="Vaucluse")
    assert all("Vaucluse" in v for v in vues)


def test_departement_declare_complete_celui_de_la_carte():
    """Le service d'archives connaît son fonds : on s'en sert quand la carte se tait."""
    corrige, _ = lieux.corriger(
        {"commune": "Pernes", "departement": "Aucun département"}, ABSENTS, "Vaucluse")
    assert corrige["departement"] == "Vaucluse"


def test_le_departement_declare_prime_sur_celui_lu_par_le_modele():
    """Le modèle lit parfois de travers ; l'archiviste, lui, connaît son fonds."""
    corrige, _ = lieux.corriger(
        {"commune": "Pernes", "departement": "Pas-de-Calais"}, ABSENTS, "Vaucluse")
    assert corrige["departement"] == "Vaucluse"
    assert corrige["commune"] == "Pernes-les-Fontaines"


def test_liste_des_departements_proposee():
    noms = lieux.liste_departements()
    assert "Vaucluse" in noms and "Gard" in noms
    assert all(nom.strip() for nom in noms)


# --- Avertissement « cookies tiers » ----------------------------------------

SAFARI_MAC = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
              "(KHTML, like Gecko) Version/18.0 Safari/605.1.15")
CHROME_MAC = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
FIREFOX_MAC = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) "
               "Gecko/20100101 Firefox/142.0")
CHROME_IOS = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
              "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/140.0 Mobile/15E148 Safari/604.1")


def test_safari_est_averti_du_403():
    """Lui seul refuse le cookie du cadre : le téléversement y échoue encore."""
    assert navigateur.refuse_les_cookies_tiers(SAFARI_MAC)
    assert navigateur.refuse_les_cookies_tiers(CHROME_IOS)


def test_les_autres_navigateurs_ne_sont_pas_avertis():
    """Chrome et Firefox cloisonnent le cookie mais l'acceptent : rien à dire."""
    assert not navigateur.refuse_les_cookies_tiers(CHROME_MAC)
    assert not navigateur.refuse_les_cookies_tiers(FIREFOX_MAC)


def test_signature_absente_pas_d_avertissement():
    """Sans en-tête User-Agent, mieux vaut se taire que crier au loup."""
    assert not navigateur.refuse_les_cookies_tiers("")
    assert not navigateur.refuse_les_cookies_tiers(None)


# --- Texte affichable --------------------------------------------------------

RACINE_SRC = Path(__file__).resolve().parent.parent / "src"


def test_aucune_chaine_de_source_n_est_indicible():
    """Une paire de substituts écrite `\\ud83d\\udccd` n'est pas un émoji.

    Écrite ainsi dans le source, elle traverse la compilation sans bruit mais
    Streamlit la refuse au moment de l'afficher (« is not a valid emoji »), et
    la page entière tombe. C'est ce qui cassait l'avertissement « département
    manquant » de la page Essayer. On vérifie que toute constante textuelle du
    source est encodable, donc réellement affichable.
    """
    import ast

    for fichier in sorted(RACINE_SRC.rglob("*.py")):
        arbre = ast.parse(fichier.read_text(encoding="utf-8"), filename=str(fichier))
        for noeud in ast.walk(arbre):
            if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str):
                try:
                    noeud.value.encode("utf-8")
                except UnicodeEncodeError:  # pragma: no cover - le test échoue
                    pytest.fail(
                        f"{fichier.name} ligne {noeud.lineno} : chaîne non encodable "
                        f"({noeud.value!r})"
                    )
