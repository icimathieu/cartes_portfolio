import json
import sys
import streamlit as st
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from footer import render_footer

st.title("🖼️ Exemples de cartes postales géolocalisées")

st.markdown("""
Voici une sélection de 20 cartes postales du corpus, toutes géolocalisées 
par la pipeline sur les trois niveaux (commune, lieu-dit, monument).
Les cas marqués **Bonus** correspondent à des cartes géolocalisées
sans texte de localisation visible — le modèle s'appuie alors sur le contenu
visuel seul ou notre système de mémorisation des cartes déjà traitées.
""")

st.markdown("---")

# --- Charger les annotations pour retrouver les métadonnées ---
annotations_path = Path("assets/benchmark/modele_seul/annotations.json")
images_dir = Path("assets/images")

if not annotations_path.exists() or not images_dir.exists():
    st.error("Données introuvables.")
    st.stop()

with open(annotations_path, encoding="utf-8") as f:
    annotations = json.load(f)

annotations_by_file = {a["File name"]: a for a in annotations}

image_files = sorted(images_dir.glob("*.jpg"))

if not image_files:
    st.warning("Aucune image trouvée dans assets/images/.")
    st.stop()

# --- Filtre ---
filter_option = st.radio(
    "Filtrer",
    ["Toutes", "Cas bonus uniquement"],
    horizontal=True,
)

def afficher_image(chemin):
    """Affiche une image, sans laisser un fichier abîmé emporter toute la page.

    Le Space a déjà servi un fichier que Pillow ne reconnaissait pas alors que
    le dépôt, lui, contenait bien un JPEG : la trace est donc écrite dans les
    journaux du conteneur, avec la taille et les premiers octets réellement
    lus, seul moyen de savoir ce que voit l'application.
    """
    try:
        st.image(str(chemin), use_container_width=True)
        return True
    except Exception as exc:
        try:
            debut = chemin.read_bytes()[:48]
            taille = chemin.stat().st_size
        except OSError:
            debut, taille = b"", 0
        print(f"[exemples] image illisible : {chemin} — {taille} octets — "
              f"début {debut!r} — {type(exc).__name__}: {exc}", flush=True)
        st.caption(f"Aperçu indisponible pour {chemin.name}.")
        return False


# --- Galerie ---
for i in range(0, len(image_files), 2):
    cols = st.columns(2)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= len(image_files):
            break
        img_path = image_files[idx]
        meta = annotations_by_file.get(img_path.name, {})

        is_bonus = meta.get("bonus") is not None

        if filter_option == "Cas bonus uniquement" and not is_bonus:
            continue

        with col:
            afficher_image(img_path)

            commune = meta.get("trans_city", "—")
            lieu_dit = meta.get("trans_hamlet_uniformise", "—")
            monument = meta.get("trans_monument_uniformise", "—")

            badge = " 🎯 **Bonus**" if is_bonus else ""

            st.markdown(
                f"**{img_path.name}**{badge}\n\n"
                f"| Niveau | Prédiction |\n"
                f"|---|---|\n"
                f"| Commune | {commune} |\n"
                f"| Lieu-dit | {lieu_dit} |\n"
                f"| Monument | {monument} |"
            )
            st.markdown("---")

st.info(
    "📄 **Code source et données** : "
    "[github.com/icimathieu/cartes_portfolio](https://github.com/icimathieu/cartes_portfolio)"
    "\n\n" \
    "✉️ **Contact** : "
    "[mathieu.riviere@chartes.psl.eu](mailto:mathieu.riviere@chartes.psl.eu) · "
    "[maxime.letoffe@chartes.psl.eu](mailto:maxime.letoffe@chartes.psl.eu)"
)

render_footer()
