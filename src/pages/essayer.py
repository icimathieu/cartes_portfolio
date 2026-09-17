import os
import sys
from pathlib import Path

import folium
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.parent))
from demo import geocode, images, modeles, quota, vlm  # noqa: E402
from footer import render_footer  # noqa: E402

MAX_IMAGES_PAR_ESSAI = 3

st.title("🔧 Essayer la pipeline")

st.markdown(
    "Téléversez une à trois de vos cartes postales : le modèle lit l'image, propose "
    "une commune, un lieu-dit et un monument, puis ces noms sont convertis en "
    "coordonnées par OpenStreetMap et placés sur une carte."
)

st.info(
    "**Démo simplifiée.** Elle travaille sur la seule image. La prestation complète "
    "croise en plus les métadonnées de votre catalogue, une cascade de géocodage à "
    "plusieurs niveaux et une relecture humaine — ce qui change nettement les "
    "résultats : voir la page Benchmark.",
    icon="ℹ️",
)

# --- Budget du jour et quota du visiteur ------------------------------------

api_key = os.environ.get("OPENROUTER_API_KEY", "")
depense = st.cache_resource(lambda: quota.Depense())()

if "images_utilisees" not in st.session_state:
    st.session_state.images_utilisees = 0
if "libelle_code" not in st.session_state:
    st.session_state.libelle_code = None
if "code_signale" not in st.session_state:
    st.session_state.code_signale = False

with st.expander("J'ai un code d'accès", expanded=False):
    st.caption(
        "Les codes figurent dans nos courriers aux services d'archives et donnent "
        f"droit à {quota.IMAGES_AVEC_CODE} images. Sans code, la démo fonctionne "
        f"quand même, dans la limite de {quota.IMAGES_ANONYME} images."
    )
    saisie = st.text_input("Code", max_chars=32, placeholder="XXXX-000")
    if st.button("Valider le code"):
        libelle = quota.verifier_code(saisie)
        if libelle:
            st.session_state.libelle_code = libelle
            st.success("Code reconnu, quota étendu.")
        else:
            st.error("Code inconnu.")

quota_total = quota.quota_images(st.session_state.libelle_code)
restantes = max(quota_total - st.session_state.images_utilisees, 0)

ouverte, message_budget, _ = quota.etat_budget(api_key, depense)
if not ouverte:
    st.warning(message_budget, icon="⏳")
elif not api_key:
    st.warning(
        "La démo est momentanément indisponible. Écrivez-nous et nous vous "
        "montrons la pipeline sur vos propres cartes.",
        icon="⏳",
    )

st.caption(f"Il vous reste **{restantes}** images sur {quota_total} pour cette visite.")

# --- Réglages de l'essai ----------------------------------------------------

col_gauche, col_droite = st.columns([3, 2])

with col_gauche:
    fichiers = st.file_uploader(
        "Vos cartes postales (JPG ou PNG)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help=f"{MAX_IMAGES_PAR_ESSAI} images au maximum par essai.",
        disabled=not (ouverte and api_key and restantes),
    )

with col_droite:
    st.markdown("**Que chercher ?**")
    champs = []
    for cle, spec in vlm.FIELDS.items():
        coche = st.checkbox(
            spec["label"],
            value=cle in vlm.DEFAULT_FIELDS,
            disabled=spec.get("locked", False),
            help="La commune est nécessaire au placement sur la carte."
            if spec.get("locked")
            else None,
        )
        if coche or spec.get("locked"):
            champs.append(cle)

    st.markdown("**Quel modèle ?**")
    choix = st.radio(
        "Modèle",
        options=list(modeles.MODELES),
        index=list(modeles.MODELES).index(modeles.DEFAUT),
        format_func=lambda c: modeles.MODELES[c]["titre"],
        label_visibility="collapsed",
    )
    st.caption(modeles.MODELES[choix]["detail"])
    prix_mille = modeles.MODELES[choix]["prix_usd_par_image"] * 1000
    st.caption(
        f"Ordre de grandeur : **{prix_mille:.2f} $ pour 1 000 cartes** avec ce modèle. "
        "Le coût réel de chaque essai est affiché sous les résultats."
    )

lancer = st.button("Analyser", type="primary", disabled=not (fichiers and ouverte and api_key))

# --- Analyse ----------------------------------------------------------------


def afficher_resultat(fichier, reponse, geo, champs_demandes):
    """Affiche une carte analysée : image, noms trouvés, carte, coût."""
    colonne_image, colonne_texte = st.columns([1, 2])
    with colonne_image:
        st.image(fichier, use_container_width=True)
    with colonne_texte:
        resultat = reponse["resultat"] or {}
        for cle in champs_demandes:
            valeur = resultat.get(cle)
            if not valeur:
                continue
            libelle = vlm.FIELDS[cle]["label"]
            if cle == "texte_imprime":
                with st.expander(f"{libelle}"):
                    st.text(valeur)
            else:
                st.markdown(f"**{libelle}** — {valeur}")
        if resultat.get("indices"):
            st.caption("Indice retenu par le modèle : " + str(resultat["indices"]))

    if geo["niveau"] == "echec":
        st.warning("Aucun lieu n'a pu être placé sur la carte pour cette image.")
    else:
        st.markdown(
            f"**Précision atteinte : {geo['libelle_niveau']}** — {geo['adresse']}"
        )
        carte = folium.Map(location=[geo["lat"], geo["lon"]], zoom_start=15,
                           tiles="OpenStreetMap")
        folium.Marker(
            [geo["lat"], geo["lon"]],
            tooltip=geo["requete"],
        ).add_to(carte)
        components.html(carte._repr_html_(), height=280)
        st.caption(geocode.ATTRIBUTION)

    details = [f"modèle : {reponse.get('modele')}"]
    if reponse.get("fournisseur"):
        details.append(f"fournisseur : {reponse['fournisseur']}")
    if reponse.get("cout_usd") is not None:
        details.append(f"coût réel de cet essai : {reponse['cout_usd']:.4f} $")
    details.append(f"durée : {reponse.get('latence_s')} s")
    st.caption(" · ".join(details))
    for rejet in geo["rejets"]:
        st.caption(f"Écarté : « {rejet['requete']} » — {rejet['raison']}")


if lancer and fichiers:
    if len(fichiers) > MAX_IMAGES_PAR_ESSAI:
        st.error(f"{MAX_IMAGES_PAR_ESSAI} images au maximum par essai.")
    elif len(fichiers) > restantes:
        st.error(
            f"Il ne vous reste que {restantes} image(s). Écrivez-nous pour un essai "
            "sur votre fonds."
        )
    else:
        if st.session_state.libelle_code and not st.session_state.code_signale:
            quota.notifier(f"{st.session_state.libelle_code} teste la démo")
            st.session_state.code_signale = True

        for fichier in fichiers:
            st.divider()
            try:
                image, _ = images.preparer_image(fichier.getvalue())
            except ValueError as exc:
                st.error(str(exc))
                continue

            with st.spinner(f"Analyse de {fichier.name}…"):
                modele = modeles.MODELES[choix]
                try:
                    reponse = vlm.analyser_carte(
                        image_bytes=image,
                        fields=champs,
                        model=modele["slug"],
                        api_key=api_key,
                    )
                except vlm.VLMError as exc:
                    st.error(str(exc))
                    if getattr(exc, "status", None) == 402:
                        quota.notifier("Budget de la démo épuisé (402 OpenRouter)")
                        depense.usage_du_jour(api_key, force=True)
                    continue

                st.session_state.images_utilisees += 1
                depense.ajouter(reponse.get("cout_usd"))
                resultat = reponse["resultat"] or {}
                geo = geocode.geocoder_cascade(
                    commune=resultat.get("commune"),
                    lieu_dit=resultat.get("lieu_dit"),
                    monument=resultat.get("monument"),
                )

            afficher_resultat(fichier, reponse, geo, champs)

        st.divider()
        st.caption(
            f"Il vous reste {max(quota_total - st.session_state.images_utilisees, 0)} "
            "images pour cette visite."
        )

# --- Mentions ---------------------------------------------------------------

st.markdown("---")

with st.expander("Ce que deviennent vos images"):
    st.markdown(
        """
- Votre image est réduite à 1024 pixels et **ses métadonnées EXIF sont retirées**
  (elles peuvent contenir les coordonnées GPS de l'appareil).
- Elle est transmise à un modèle via **OpenRouter**, qui ne conserve ni les requêtes
  ni les réponses. Chaque appel **impose des fournisseurs qui s'engagent à ne rien
  conserver** et exclut ceux qui collectent les données pour entraîner leurs modèles.
- **Nous ne gardons rien** : ni image, ni résultat, ni adresse, ni compte. Rien n'est
  écrit sur un disque, et recharger la page efface tout.
- Les coordonnées viennent de **Nominatim / OpenStreetMap**, interrogé avec les seuls
  noms de lieux, jamais avec votre image.
- Pour un fonds sensible, la pipeline peut tourner **entièrement sur nos machines ou
  sur un serveur français ou européen**, avec un modèle à poids ouverts : dans ce cas
  aucune donnée ne sort de l'infrastructure choisie.
        """
    )

st.info(
    "📄 **Code source et données** : "
    "[github.com/icimathieu/cartes_portfolio](https://github.com/icimathieu/cartes_portfolio)"
    "\n\n"
    "✉️ **Contact** : "
    "[mathieu.riviere@chartes.psl.eu](mailto:mathieu.riviere@chartes.psl.eu) · "
    "[maxime.letoffe@chartes.psl.eu](mailto:maxime.letoffe@chartes.psl.eu)"
)

render_footer()
