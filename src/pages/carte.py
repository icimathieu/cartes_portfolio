import streamlit as st
from pathlib import Path

st.title("🗺️ Carte interactive des cartes postales")

st.markdown("""
Cette carte présente l'ensemble des cartes postales géolocalisées par la pipeline.
Chaque marqueur correspond à une carte postale dont la commune, le lieu-dit
et/ou le monument ont été identifiés automatiquement puis géoréférencés.

> *Cette carte sera également diffusée sur le site des
> [Archives départementales du Vaucluse](https://archives.vaucluse.fr/).*
""")

st.markdown("---")

carte_path = Path("assets/carte/carte_vaucluse_interactive5.html")

if carte_path.exists():
    html_content = carte_path.read_text(encoding="utf-8")
    st.components.v1.html(html_content, height=700, scrolling=True)
else:
    st.error("Fichier carte introuvable.")
