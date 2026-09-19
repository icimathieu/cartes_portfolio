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
    - 🤖 **Choix du modèle d'IA** : local (confidentialité maximale, Qwen2.5-VL) ou
      distant (Gemini, plus performant mais via les serveurs Google)
    - 📦 **Cession du code** et documentation pour maintenance interne
    """)

st.markdown("---")

# --- Budget ---
st.subheader("Quel budget prévoir ?")

st.markdown("""
Les prestations des junior-entreprises se comptent en **JEH** (journée étude
homme) : une journée de travail d'un étudiant membre de l'association, facturée
**250 €** chez nous. Une prestation « cartes postales » représente quelques
journées de travail pour chacun d'entre nous, ce qui place le devis dans une
fourchette de **1 000 à 2 000 €**.

Ce qui fait varier le montant :
""")

col_budget_a, col_budget_b = st.columns(2)

with col_budget_a:
    st.markdown("""
    - 📚 **Le volume du fonds** et l'état de sa numérisation
    - 🗂️ **La qualité des métadonnées** existantes
    """)

with col_budget_b:
    st.markdown("""
    - ⚙️ **Les options retenues** ci-dessus (numérisation, modèle local,
      intégration au site, cession du code)
    - 🎯 **Le niveau de précision** attendu et l'ampleur de la relecture
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

Le travail est aujourd'hui **publié par les Archives départementales de
Vaucluse** : 2 779 des 2 928 cartes du fonds figurent sur
[la carte diffusée par le Département](https://maps.vaucluse.fr/index.php/view/map?repository=archives&project=cartes_postales_vaucluse),
à laquelle les Archives ont consacré un billet,
[« Album de Vaucluse : le territoire révélé en cartes postales »](https://memento.vaucluse.fr/toutes-les-ressources/album-de-vaucluse-les-cartes-postales-revelent-le-territoire).

Nous appliquons les mêmes méthodes hors du champ des cartes postales. Nous avons
animé un **atelier de spatialisation** lors de l'école d'été internationale
[*De la fermeture au partage : exploration des données de recherche sur le
patrimoine de l'Afghanistan et des pays voisins*](https://www.inalco.fr/actualites/de-la-fermeture-au-partage-une-ecole-dete-internationale-consacree-au-patrimoine-de)
(juin 2026, avec le consortium
[Distam+](https://etudes-areales.cnrs.fr/programme-summer-school/)), sur un fonds
photographique concernant les provinces iraniennes : lecture automatique des
légendes en persan, puis localisation. Le code est
[ouvert](https://github.com/icimathieu/atelier_spatialisation_INHA).

C'est un projet très enrichissant, qui nous permet de mobiliser des outils
récents et performants que nous rencontrons par ailleurs durant nos cours.
C'est aussi une façon pour nous de valoriser nos compétences et d'avoir
une formation très empirique !
""")

st.markdown("---")

# --- CartaData ---
st.subheader("Un cadre institutionnel : CartaData")

st.markdown("""
Nous intervenons dans le cadre de **[CartaData](https://www.chartes.psl.eu/vie-de-campus/vie-etudiante-et-associative/cartadata)**,
la junior-entreprise de l'École nationale des chartes — PSL, fondée en 2025 et
coordonnée par Chahan Vidal-Gorène, directeur du master *Humanités numériques*.

CartaData met les compétences académiques de ses membres au service
d'institutions patrimoniales et d'acteurs privés, autour de trois pôles :

- **Transcription** : transcription manuelle ou automatisée (français, latin),
  recherche bibliographique, catalogage, conseil en numérisation
- **Données** : structuration (XML, JSON, CSV), nettoyage de jeux de données,
  web-scraping, interrogation d'API, visualisation
- **Conseil** : analyse des besoins, stratégies de valorisation, modélisation
  de bases, intégration d'outils d'IA

S'appuyer sur CartaData, c'est pour vous l'assurance d'un **cadre
administratif et juridique sûr** : conventions, facturation, comptabilité
et responsabilités sont pris en charge par l'association, sous la
supervision de l'École. Vous contractez avec une structure reconnue,
adossée à un établissement du groupe PSL.
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

🏛️ **CartaData**, la junior-entreprise qui porte la prestation :
[présentation sur le site de l'École nationale des chartes](https://www.chartes.psl.eu/vie-de-campus/vie-etudiante-et-associative/cartadata)
""")

st.markdown("---")

st.info(
    "📄 **Code source et données du projet ** : "
    "[github.com/icimathieu/vaucluse](https://github.com/icimathieu/cartes_portfolio)"
)

render_footer()
