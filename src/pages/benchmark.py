import streamlit as st
from pathlib import Path

st.title("📊 Benchmark — 600 cartes postales")

st.markdown("""
Le benchmark évalue la pipeline sur un corpus annoté manuellement de **600 cartes
postales**. Chaque carte est jugée sur trois niveaux : commune, lieu-dit et monument.
Les 8 cas intrinsèquement ambigus sont exclus, soit un corpus final de **592 cartes**.

Trois configurations sont comparées :
""")

# --- Sélecteur de configuration ---
CONFIGS = {
    "Modèle seul": {
        "key": "modele_seul",
        "desc": (
            "Le modèle VLM (Gemini) analyse la carte postale sans aucune information "
            "contextuelle. C'est la configuration la plus exigeante."
        ),
    },
    "Avec commune scrapée": {
        "key": "avec_commune",
        "desc": (
            "La commune d'origine, lorsqu'elle est disponible dans les métadonnées "
            "de l'archive, est fournie au modèle comme contexte supplémentaire."
        ),
    },
    "Avec édifice + commune": {
        "key": "avec_edifice_commune",
        "desc": (
            "Le nom de l'édifice et la commune, lorsqu'ils sont disponibles dans les "
            "métadonnées de l'archive, sont fournis au modèle."
        ),
    },
}

selected_label = st.selectbox(
    "Configuration",
    list(CONFIGS.keys()),
)

config = CONFIGS[selected_label]
config_dir = Path(f"assets/benchmark/{config['key']}")

st.info(config["desc"])

# --- Chiffres clés du pitch summary ---
summary_path = config_dir / "benchmark_pitch_summary.md"
if summary_path.exists():
    summary_text = summary_path.read_text(encoding="utf-8")

    # Extraire les chiffres clés de la section ## Chiffres
    lines = summary_text.split("\n")
    for line in lines:
        if "Cartes entierement correctes" in line:
            pct = line.split(":")[-1].strip()
            st.metric("Cartes entièrement correctes sur 3 niveaux", pct)
            break

st.markdown("---")

# --- Plots ---
st.subheader("Résultats détaillés")

PLOT_LABELS = {
    "01_overview_by_level.png": "Vue d'ensemble par niveau",
    "04_card_level_summary.png": "Lecture exécutive",
    "06_recall_proxy.png": "Rappel proxy par niveau",
    "05_bonus_cases.png": "Cas bonus (géolocalisation sans texte)",
    "03_error_types.png": "Types d'erreurs",
    "02_status_split.png": "Répartition correct / erreur / manquant",
    "07_cross_errors.png": "Erreurs croisées et swaps",
    "08_error_types_pct.png": "Types d'erreurs (%)",
    "09_quality_metrics_by_category.png": "Métriques de qualité par catégorie",
}

# Ordre d'affichage privilégié
PLOT_ORDER = [
    "01_overview_by_level.png",
    "04_card_level_summary.png",
    "06_recall_proxy.png",
    "05_bonus_cases.png",
    "03_error_types.png",
    "02_status_split.png",
    "07_cross_errors.png",
    "08_error_types_pct.png",
    "09_quality_metrics_by_category.png",
]

plots_dir = config_dir / "plots"
if plots_dir.exists():
    available_plots = {p.name: p for p in plots_dir.glob("*.png")}

    for plot_name in PLOT_ORDER:
        if plot_name in available_plots:
            label = PLOT_LABELS.get(plot_name, plot_name)
            with st.expander(label, expanded=(plot_name in [
                "01_overview_by_level.png",
                "04_card_level_summary.png",
            ])):
                st.image(str(available_plots[plot_name]), use_container_width=True)
else:
    st.warning("Plots introuvables pour cette configuration.")

# --- Lecture client ---
st.markdown("---")
st.subheader("Lecture client")

if summary_path.exists():
    # Extraire la section Lecture client
    in_section = False
    client_lines = []
    for line in lines:
        if "## Lecture client" in line or "### 1." in line:
            in_section = True
            if "### 1." in line:
                client_lines.append(line)
            continue
        if in_section:
            client_lines.append(line)

    if client_lines:
        st.markdown("\n".join(client_lines))
    else:
        st.info("Section de lecture client non disponible pour cette configuration.")

# --- Accès au notebook ---
st.markdown("---")
st.caption(
    "📓 Le notebook complet de benchmark est disponible dans le dépôt : "
    "[benchmark_300_cartes_vaucluse.ipynb]"
    "(https://github.com/icimathieu/cartes_portfolio/blob/main/"
    "assets/benchmark/benchmark_300_cartes_vaucluse.ipynb)"
)
