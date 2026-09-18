import os
import sys
from pathlib import Path

import folium
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.parent))
from demo import geocode, images, lieux, modeles, quota, vlm  # noqa: E402
from footer import render_footer  # noqa: E402

MAX_IMAGES_PAR_ESSAI = 5

st.title("🔧 Essayer la pipeline")

st.markdown(
    "Téléversez vos cartes postales et indiquez le département de votre service "
    "d'archives : le modèle lit l'image et propose une commune, un lieu-dit et un "
    "monument. Ces noms sont vérifiés contre les communes du département que vous "
    "avez choisi, puis convertis en coordonnées par OpenStreetMap et placés sur une "
    "carte."
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

quota_total = quota.quota_images(st.session_state.libelle_code)
restantes = max(quota_total - st.session_state.images_utilisees, 0)

ouverte, message_budget, _ = quota.etat_budget(api_key, depense)
if not ouverte:
    st.warning(message_budget, icon="\u23f3")
elif not api_key:
    st.warning(
        "La d\u00e9mo est momentan\u00e9ment indisponible. \u00c9crivez-nous et nous vous "
        "montrons la pipeline sur vos propres cartes.",
        icon="\u23f3",
    )

st.caption(f"Il vous reste **{restantes}** images sur {quota_total} pour cette visite.")

with st.expander("J\u2019ai un code d\u2019acc\u00e8s", expanded=False):
    st.caption(
        "Les codes figurent dans nos courriers aux services d\u2019archives et donnent "
        f"droit \u00e0 {quota.IMAGES_AVEC_CODE} images. Sans code, la d\u00e9mo fonctionne "
        f"quand m\u00eame, dans la limite de {quota.IMAGES_ANONYME} images."
    )
    saisie = st.text_input("Code", max_chars=32, placeholder="XXXX-000")
    if st.button("Valider le code"):
        libelle = quota.verifier_code(saisie)
        if libelle:
            st.session_state.libelle_code = libelle
            st.success("Code reconnu, quota \u00e9tendu.")
        else:
            st.error("Code inconnu.")

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

    st.info(
        "**Cette d\u00e9mo ne voit que l\u2019image et le d\u00e9partement que vous indiquez.** "
        "Notre cha\u00eene de traitement compl\u00e8te y ajoute les m\u00e9tadonn\u00e9es de votre "
        "catalogue, un g\u00e9ocodage en cascade qui croise ces sources et une "
        "v\u00e9rification. Mesur\u00e9 sur notre benchmark, l\u2019\u00e9cart porte surtout sur **la "
        "pr\u00e9cision du point pos\u00e9 sur la carte** : la cha\u00eene compl\u00e8te situe **trois "
        "fois plus** de cartes sur le b\u00e2timent exact, **divise par deux** le nombre de "
        "celles qui n\u2019arrivent pas plus loin que la commune, et **par pr\u00e8s de trois** "
        "le nombre de cartes mal plac\u00e9es. Les chiffres sont sur la page Benchmark.\n\n"
        "\U0001f6a7 En cours de d\u00e9veloppement, donc absent de la cha\u00eene mesur\u00e9e : une "
        "recherche automatis\u00e9e sur le web et sur les bases patrimoniales (M\u00e9rim\u00e9e, "
        "POP, Wikidata) pour identifier les \u00e9difices que le catalogue ne nomme pas.",
        icon="\u2139\ufe0f",
    )

with col_droite:
    st.markdown("**Que chercher ?**")
    champs = list(vlm.CHAMPS_CACHES)
    for cle, spec in vlm.FIELDS.items():
        if spec.get("cache"):
            continue
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

    st.markdown("**De quel service d'archives viennent ces cartes ?** *(obligatoire)*")
    departement_declare = st.selectbox(
        "Département du service d'archives",
        options=lieux.liste_departements(),
        index=None,
        placeholder="Choisissez un département",
        label_visibility="collapsed",
        help="Notre chaîne de traitement restreint alors la recherche aux communes "
             "de ce département. Sans cette indication, une carte peut atterrir à "
             "900 km : « Pernes » existe dans le Pas-de-Calais et en Vaucluse.",
    )
    if departement_declare:
        st.caption(
            f"La recherche sera restreinte aux "
            f"**{len(lieux.communes_du_departement(departement_declare))} communes** "
            "de ce département : n'envoyez que des cartes de ce fonds."
        )

    st.markdown("**Quel modèle ?**")
    choix = st.radio(
        "Modèle",
        options=list(modeles.MODELES),
        index=list(modeles.MODELES).index(modeles.DEFAUT),
        format_func=lambda c: modeles.MODELES[c]["titre"],
        label_visibility="collapsed",
    )
    st.caption(modeles.MODELES[choix]["detail"])

col_bouton, col_rappel = st.columns([1, 4])

with col_bouton:
    lancer = st.button(
        "Analyser",
        type="primary",
        disabled=not (fichiers and departement_declare and ouverte and api_key),
    )

with col_rappel:
    if not departement_declare:
        st.caption(
            ":orange[Indiquez le service d\u2019archives d\u2019o\u00f9 viennent ces cartes pour "
            "activer l\u2019analyse.]"
        )

# --- Analyse ----------------------------------------------------------------


def afficher_resultat(fichier, reponse, geo, champs_demandes, corrections=()):
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
        for correction in corrections:
            st.caption("Vérifié sur le référentiel officiel des communes : " + correction)

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

    # Ni le nom du fournisseur, ni les requêtes OpenStreetMap infructueuses :
    # ce sont des détails d'atelier, sans intérêt pour un archiviste.


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

                # Le modèle confond parfois les niveaux (un département donné
                # pour une commune) : le référentiel officiel des communes
                # remet les noms à leur place avant le géocodage.
                resultat, corrections = lieux.corriger(
                    reponse["resultat"] or {},
                    {cle: spec["absent"] for cle, spec in vlm.FIELDS.items()},
                    departement_declare,
                )
                reponse["resultat"] = resultat
                departement = resultat.get("departement")
                geo = geocode.geocoder_cascade(
                    commune=resultat.get("commune"),
                    lieu_dit=resultat.get("lieu_dit"),
                    monument=resultat.get("monument"),
                    departement=departement,
                    ancre=lieux.coordonnees(resultat.get("commune"), departement),
                )

            afficher_resultat(fichier, reponse, geo, champs, corrections)

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
- **Nous ne gardons rien** : ni image, ni résultat, ni adresse, ni compte, ni le
  département que vous indiquez. Rien n'est écrit sur un disque, et recharger la page
  efface tout.
- Les noms de communes sont vérifiés contre le **référentiel officiel des communes
  françaises**, embarqué dans l'application et restreint au département que vous
  indiquez : rien n'est envoyé nulle part pour ça.
- Les coordonnées viennent de **Nominatim / OpenStreetMap**, interrogé avec les seuls
  noms de lieux détectés, jamais avec votre image.
- Pour votre fonds, la pipeline peut tourner **entièrement sur nos machines ou sur un
  serveur français**, avec un modèle à poids ouverts : dans ce cas aucune donnée ne
  sort de l'infrastructure choisie.
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
