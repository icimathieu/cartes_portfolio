import streamlit as st

st.title("Géolocalisation automatique de cartes postales anciennes")
st.subheader("Archives départementales du Vaucluse")

st.markdown("---")

# --- Pitch ---
st.markdown("""
Ce projet propose une **pipeline de géolocalisation automatique** appliquée à un corpus
de cartes postales anciennes numérisées par les Archives départementales du Vaucluse.

À partir de la seule image d'une carte postale, la pipeline identifie automatiquement
trois niveaux de localisation :
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Commune", "91,4 %", help="Exactitude sur cartes couvertes")
with col2:
    st.metric("Lieu-dit", "91,6 %", help="Exactitude sur cartes couvertes")
with col3:
    st.metric("Monument", "89,4 %", help="Exactitude sur cartes couvertes")

st.markdown("---")

# --- Schéma pipeline ---
st.subheader("La pipeline en un coup d'œil")

st.markdown("""
```
   Image carte postale
          │
          ▼
   ┌──────────────┐
   │  Scraping     │  Récupération des images et métadonnées
   │  Archives 84  │  depuis les fonds numérisés
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Modèle VLM  │  Analyse visuelle et textuelle
   │  (Gemini)    │  de chaque carte postale
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Géoréféren- │  Résolution des toponymes
   │  cement      │  et coordonnées GPS
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Carte       │  Visualisation interactive
   │  interactive │  des résultats
   └──────────────┘
```
""")

st.markdown("---")

# --- Chiffres clés ---
st.subheader("Chiffres clés")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Cartes traitées", "600")
with col2:
    st.metric("Correctes (3 niveaux)", "76,7 %")
with col3:
    st.metric("Hallucinations", "1,01 %")
with col4:
    st.metric("Cas bonus", "31", help="Cartes géolocalisées sans texte de localisation visible")

st.markdown("""
> Le benchmark complet porte sur **592 cartes** (8 cas ambigus exclus sur 600).
> Les résultats ci-dessus correspondent à la configuration **modèle seul**,
> sans information contextuelle supplémentaire.
""")

st.info(
    "📄 **Code source et données** : "
    "[github.com/icimathieu/cartes_portfolio](https://github.com/icimathieu/cartes_portfolio)"
)
