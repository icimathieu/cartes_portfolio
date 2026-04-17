import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from footer import render_footer

st.title("🤝 Notre offre")

st.markdown("""
Nous adaptons à votre fonds la chaîne de traitement conçue pour les Archives
départementales du Vaucluse : de l'image brute à une **carte web interactive
prête à intégrer** sur votre site. Vous nous confiez un corpus, vous récupérez
un livrable.

Les résultats obtenus sur le Vaucluse sont consultables dans les pages
[**Carte interactive**](/carte) et [**Benchmark**](/benchmark), avec une
sélection illustrée dans [**Exemples**](/exemples).
""")

st.markdown("---")

# --- Proposition clés en main ---
st.subheader("Clés en main, de l'image au livrable")

st.markdown("""
Nous prenons en charge l'ensemble du processus. Chaque étape peut être réalisée
par nous ou restituée à vos équipes, selon votre préférence.
""")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    **1. Récupération du corpus**
    Nous collectons les images et leurs métadonnées depuis votre site d'archives,
    ou directement depuis un lot que vous nous transmettez.

    **2. Analyse par IA vision-langage**
    Notre chaîne interroge un modèle multimodal sur chaque carte postale pour
    identifier, lorsqu'ils sont lisibles, la commune, le lieu-dit et le monument.

    **3. Consolidation et géoréférencement**
    Croisement avec des bases toponymiques et patrimoniales (Mérimée, TOPO,
    OpenStreetMap), garde-fous pour limiter les hallucinations, résolution des
    coordonnées GPS.
    """)

with col2:
    st.markdown("""
    **4. Production de la carte interactive**
    Une carte HTML autonome, navigable par décennies, avec vignettes, liens vers
    les notices d'archives et filtres par niveau de précision.

    **5. Livraison et intégration**
    Vous recevez la carte sous forme de fichier intégrable, ou nous nous chargeons
    de l'insérer directement sur votre site en lien avec vos équipes techniques.

    **6. Documentation et transfert**
    Guide d'évaluation, benchmark dédié à votre corpus, et — si vous le souhaitez —
    cession du code accompagnée d'un temps d'échange avec vos archivistes.
    """)

st.markdown("---")

# --- Options ---
st.subheader("Des options selon vos besoins")

st.markdown("""
La prestation de base produit une carte interactive à partir de cartes postales
déjà numérisées. Elle peut être étoffée :
""")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    - 📸 **Numérisation préalable** de cartes postales non encore dématérialisées
    - 🖼️ **Collecte des images** sur votre site si votre infrastructure le permet
    - 🔍 **Ajustement des niveaux de précision** : commune, lieu-dit, monument,
      ou plus fin
    """)

with col_b:
    st.markdown("""
    - 🤖 **Choix du modèle d'IA** : local (confidentialité maximale, QWEN3-VL) ou
      distant (Gemini, plus performant mais via les serveurs Google)
    - 🌐 **Intégration au site** par nos soins, en lien avec vos équipes
    - 📦 **Cession du code** et documentation pour maintenance interne
    """)

st.markdown("---")

# --- Pourquoi nous ? ---
st.subheader("Qui sommes-nous ? ")

st.markdown("""
Nous sommes deux étudiants du master *Humanités numériques* de l'**École
nationale des chartes — PSL**, formation qui croise sciences humaines et sociales,
archivistique et humanités numériques.

Ce projet est né lors du **hackathon 2026** organisé en partenariat avec les
Archives départementales du Vaucluse. À l'issue de la semaine, le prototype a
suffisamment convaincu pour que nous décidions de poursuivre le chantier sur
notre temps personnel : consolidation de la chaîne, benchmark sur 600 cartes annotées,
intégration finale sur le site des Archives, rédaction d'un billet,
documentation, généralisation de la méthode, etc.
            
C'est un projet très enrichissant, qui nous permet de mobiliser des outils 
récents et performants que nous rencontrons par ailleurs durant nos cours. 
C'est aussi une façon pour nous de valoriser nos compétences et d'avoir 
une formation très empirique ! 
""")

st.markdown("---")

# --- Contact ---
st.subheader("Discutons")

st.markdown("""
Si une telle démarche vous intéresse, nous serions ravis
d'échanger lors d'un court rendez-vous pour vous présenter le projet et/ou
envisager un **pilote sur un échantillon** de votre corpus.

✉️ **Contact** :
[mathieu.riviere@chartes.psl.eu](mailto:mathieu.riviere@chartes.psl.eu) · [maxime.letoffe@chartes.psl.eu](mailto:maxime.letoffe@chartes.psl.eu)
""")

st.markdown("---")

st.info(
    "📄 **Code source et données du projet ** : "
    "[github.com/icimathieu/vaucluse](https://github.com/icimathieu/cartes_portfolio)"
)

render_footer()
