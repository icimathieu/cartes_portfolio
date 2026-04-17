import streamlit as st

st.set_page_config(
    page_title="Cartes Postales du Vaucluse",
    page_icon="🗺️",
    layout="wide",
)

accueil = st.Page("pages/accueil.py", title="Accueil", icon="🏠", default=True)
carte = st.Page("pages/carte.py", title="Carte interactive", icon="🗺️")
exemples = st.Page("pages/exemples.py", title="Exemples", icon="🖼️")
benchmark = st.Page("pages/benchmark.py", title="Benchmark", icon="📊")
offre = st.Page("pages/offre.py", title="Notre offre", icon="🤝")
essayer = st.Page("pages/essayer.py", title="Essayer la pipeline", icon="🔧")

nav = st.navigation([accueil, carte, exemples, benchmark, offre, essayer])
nav.run()
