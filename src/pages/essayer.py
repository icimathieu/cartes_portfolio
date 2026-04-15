import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from footer import render_footer

st.title("🔧 Essayer la pipeline")

st.markdown("""
> **Cette page est en construction.**
>
> À terme, vous pourrez téléverser une image de carte postale et obtenir
> en retour les prédictions de la pipeline (commune, lieu-dit, monument)
> via un appel API.
""")

st.divider()

st.markdown("""
### Fonctionnement prévu

1. **Téléverser** une image de carte postale (JPG, PNG)
2. La pipeline analyse l'image via le modèle VLM
3. **Résultat** : commune, lieu-dit et monument prédits,
   avec coordonnées GPS et niveau de confiance
""")

st.divider()

# Placeholder désactivé
st.file_uploader(
    "Téléverser une carte postale",
    type=["jpg", "jpeg", "png"],
    disabled=True,
    help="Fonctionnalité à venir",
)

st.caption("Revenez bientôt — cette fonctionnalité sera disponible dans une prochaine version.")

st.markdown("---")
st.info(
    "📄 **Code source et données** : "
    "[github.com/icimathieu/cartes_portfolio](https://github.com/icimathieu/cartes_portfolio)"
    "\n\n" \
    "✉️ **Contact** : "
    "[mathieu.rivere@chartes.psl.eu](mailto:mathieu.rivere@chartes.psl.eu) · "
    "[maxime.letoffe@chartes.psl.eu](mailto:maxime.letoffe@chartes.psl.eu)"
)

render_footer()
