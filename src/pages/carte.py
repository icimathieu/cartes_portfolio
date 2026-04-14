import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from footer import render_footer

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

st.markdown("---")
st.info(
    "📄 **Code source et données** : "
    "[github.com/icimathieu/cartes_portfolio](https://github.com/icimathieu/cartes_portfolio)"
    "\n\n✉️ Contact : "
    "[mathieu.rivere@chartes.psl.eu](mailto:mathieu.rivere@chartes.psl.eu) · "
    "[maxime.letoffe@chartes.psl.eu](mailto:maxime.letoffe@chartes.psl.eu)"
)

render_footer()
