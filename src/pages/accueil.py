import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from footer import render_footer

st.title("Géolocalisation automatique de cartes postales anciennes")
st.subheader("Archives départementales du Vaucluse")

st.markdown("---")

# --- Pitch ---
st.markdown("""
Ce projet propose une **chaîne de traitement de géolocalisation automatique** appliquée à un corpus
de cartes postales anciennes numérisées par les Archives départementales du Vaucluse.

À partir de la seule image d'une carte postale, notre modèle d'intelligence artificielle open-source 
identifie automatiquement trois niveaux de localisation :
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Commune", "91,4 %", help="Exactitude sur cartes couvertes")
with col2:
    st.metric("Lieu-dit", "91,6 %", help="Exactitude sur cartes couvertes")
with col3:
    st.metric("Monument", "89,4 %", help="Exactitude sur cartes couvertes")


st.markdown("""
Notre chaîne complète quant à elle, incluant de l'extraction de métadonnées, nous permet d'atteindre les scores suivants : 
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Commune", "100 %", help="Exactitude sur cartes couvertes")
with col2:
    st.metric("Lieu-dit", "91,6 %", help="Exactitude sur cartes couvertes")
with col3:
    st.metric("Monument", "95,3 %", help="Exactitude sur cartes couvertes")

st.markdown("---")

# --- Schéma pipeline ---
st.subheader("La pipeline en un coup d'œil :")

st.markdown("""
```
   Image carte postale
          │
          ▼
   ┌──────────────┐
   │ Moissonnage  │  Récupération des images et métadonnées
   │site Archives │  depuis les fonds numérisés
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Modèle VLM  │  Analyse visuelle et textuelle
   │    (QWEN)    │  de chaque carte postale
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Géoréférence-│  Résolution des toponymes
   │  cement      │  et coordonnées GPS
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Carte       │  Visualisation interactive
   │  interactive │  des résultats
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Intégration │  Disponibilité pour les 
   │  sur site    │  usagers
   └──────────────┘
```
""")

st.markdown("---")

# --- Chiffres clés ---
st.subheader("Chiffres clés de l'évaluation de notre méthode :")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Cartes traitées", "600")
with col1:
    st.metric("Pourcentage du corpus évalué", "20%")
with col2:
    st.metric("Correctes (3 niveaux)", "87,3 %")
with col3:
    st.metric("Hallucinations", "0,23 %")
with col4:
    st.metric("Cas bonus", "31", help="Cartes géolocalisées sans texte de localisation visible grâce aux compétences du modèle ou à des mécanismes de mémoire implémentés par nos soins.")

st.markdown("""
> Le benchmark complet porte sur **592 cartes** (8 cas ambigus exclus sur 600).
> Les résultats ci-dessus correspondent à la configuration **chaîne de traitement complète**.
""")

st.markdown("---")

st.subheader("Offre de service : ")
# --- offre ---
st.markdown("""
Capables d'adapter cette chaîne de traitement à un jeu spécifique de cartes postales, nous proposons, à partir d'un set d'images, 
de réaliser l'ensemble des tâches décrites ci-dessus jusqu'à produire une carte web interactive. Les niveaux de précision, le géoréférencement ou autre
peuvent être personnalisés. De même, nous pourrions utiliser de meilleurs modèles d'IA, numériser certaines archives, céder notre code en le
discutant et l'expliquant avec des archivistes. 
            
Si une telle proposition vous intéresse, contactez : [mathieu.riviere@chartes.psl.eu](mailto:mathieu.riviere@chartes.psl.eu) ou [maxime.letoffe@chartes.psl.eu](mailto:maxime.letoffe@chartes.psl.eu)
""")


st.info(
    "📄 **Code source et données du projet original** : "
    "[github.com/icimathieu/vaucluse](https://github.com/icimathieu/vaucluse)"
)

render_footer()
