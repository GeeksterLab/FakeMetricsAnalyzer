# app.py

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from src.data_preparation import get_clean_data, add_features, normalize_features
from src.anomaly_detection import detect_anomalies
from src.visualization import interactive_plot_distribution, interactive_plot_metrics


# ====================================
# 1. Chargement et Préparation des Données
# ====================================
st.title("Dashboard Fake Metrics")

st.header("1. Chargement et Préparation des Données")
st.markdown("""
**But :**  
Charger le dataset, générer de nouvelles features et normaliser les valeurs pour pouvoir effectuer une analyse cohérente.

**Ce que vous voyez :**  
- Un aperçu des premières lignes du dataset.
- Les statistiques descriptives qui donnent une idée de la répartition des valeurs.

- la détection d'anomalies dans les données, en identifiant les points qui s'écartent significativement de la tendance générale.
- La normalisation des données pour faciliter la comparaison entre les différentes métriques.
""")

# Load and prepare the dataset
data = get_clean_data(n_samples=500, save_if_generated=True)
data = add_features(data)
data = normalize_features(data)
data = detect_anomalies(data, contamination=0.05)

# Dislay an overview of the dataset
st.write("### Aperçu du dataset", data.head())
st.markdown("""
**Description du dataset :**
- **views** : Nombre de vues sur la vidéo (standardisées).
- **likes** : Nombre de likes sur la vidéo (standardisées).
- **like-view-ratio** : Ratio brut likes / views.
- **anomaly** : Indicateur binaire : 0 = normal, 1 = anomalie.

**Lecture des données :**
- **views et likes** : Comme ils ont été standardisés, leur moyenne est proche de 0 dans l’ensemble du dataset.
    - Une valeur négative (exemple : -1.356) signifie que cette observation est environ 1,356 écarts-types en dessous de la moyenne. 
            
    - À l’inverse, une valeur positive (exemple : 1.3865) est au-dessus de la moyenne.
- **like_views_ratio** : C’est le ratio likes/views sur les données brutes (ou potentiellement après un certain prétraitement). Une valeur de 0.63 signifie qu’on a ~63% de likes par rapport aux vues sur cet enregistrement.\n
    - Si ce ratio dépasse 1, c’est qu’il y a plus de likes que de vues pour la ligne concernée (situation considérée souvent anormale). 
            
- **anomaly = 0 ou 1** : C’est la sortie de ton algorithme de détection d’anomalies (Isolation Forest, LOF, etc.).
    - 0 : observation considérée comme normale.
            
    - 1 : observation considérée comme anormale (par exemple, un post avec likes > views).

**Conclusion :**  
Dans les 5 premières lignes, anomaly est 0 partout, donc ces observations sont considérées normales par l’algorithme.
""")            

st.write("### Statistiques descriptives", data.describe())
st.markdown("""
**Description des statistiques :**
- **count** : Nous avons 1000 lignes d'observations dans le dataset.
            
- **mean** : 
    - views ≈ 0.0005, likes ≈ 1.0005 : après standardisation, on s’attend à ce que la moyenne soit proche de 0, mais il peut y avoir un léger décalage selon les données.
            
    - like_view_ratio ≈ 0.5199 : en moyenne, on a ~52% de likes par rapport aux vues (dans la version brute ou calculée).
            
    - anomaly ≈ 0.05 : environ 5% des observations sont considérées comme anomalies (c’est cohérent avec un paramètre contamination=0.05 dans Isolation Forest ou LOF). 
            
- **std (écart-type)** :
    - views ≈ 1.000 et likes ≈ 1.000 : indique que la standardisation a bien ramené l’écart-type autour de 1.
            
    - like_view_ratio ≈ 0.2571 : la répartition autour de la moyenne 0.52.
            
    - anomaly ≈ 0.2181 : pas vraiment un sens « écart-type » pour un booléen, mais c’est la dispersion de la variable 0/1.
            
- **min, 25%, 50%, 75% et max** :
    - views et likes : la valeur min de views est -1.712 (≈1,712 écarts-types sous la moyenne), la max est 1.7013, etc.
            
    - like_view_ratio : varie entre ~0.0938 et ~1.2371. Au-delà de 1, c’est plus de likes que de vues.
            
    - anomaly : min=0, max=1. Les quartiles sont 0 → cela signifie que 25%, 50% et 75% des données (les 3 quarts) sont normales, et seuls les plus gros extrêmes forment les 5% d’anomalies (valeur 1).
            

**Lecture des données :**

**Conclusion :**  
Dans les 5 premières lignes, anomaly est 0 partout, donc ces observations sont considérées normales par l’algorithme.
""")  
# ====================================
# 2. Analyse visuelle : Scatter Plot
# ====================================
st.header("2. Scatter Plot Interactif des Vues vs Likes")
st.markdown("""
**But :**  
Le scatter plot met en évidence la relation entre vues et likes, et permet de repérer visuellement les observations qui s’écartent de la tendance générale (les anomalies).
            
**Ce que vous voyez :**  
- Un graphique montrant chaque observation par rapport à ses vues et likes.
- La couleur différencie les observations normales (en bleu) et les anomalies (en rouge).
            
**Lecture des données :**
- **Axes et Échelles** : 
    - L’axe des x représente les vues (standardisées) :
        - Une valeur négative (< 0) indique que l’observation est en dessous de la moyenne des vues (en écarts-types).
            
        - Une valeur positive (> 0) indique qu’elle est au-dessus de la moyenne.
    - L’axe des y représente les likes (standardisés) :
        - Ici aussi, 0 est la moyenne, et les valeurs négatives ou positives se situent respectivement en dessous ou au-dessus de cette moyenne.
            
- **Lecture du Scatter** :
    - Nuage de points (Scatter) :
Chaque point correspond à une observation (par exemple, un post ou une vidéo).
        - Les points plus à gauche (valeurs x négatives) sont des posts ayant moins de vues que la moyenne.
        
        - Les points plus à droite (valeurs x positives) ont plus de vues que la moyenne.
            
        - De même, en bas (y négatif) = moins de likes que la moyenne, en haut (y positif) = plus de likes que la moyenne.
    - Coloration Normal / Anomaly :
        - Normal : Le point est considéré comme « cohérent » selon l’algorithme d’anomalie (Isolation Forest, LOF…).
            
        - Anomaly : Le point est jugé inhabituel (par exemple, un post ayant beaucoup plus/moins de likes qu’attendu pour son nombre de vues).
            
**Conclusion :**  
Les anomalies sont clairement identifiées et indiquent des incohérences potentielles (par exemple, des likes supérieurs aux vues).
- En général, on observe une tendance croissante (plus il y a de vues, plus il y a de likes).
- Les points colorés différemment (Anomaly) indiquent des observations que l’algorithme juge peu probables (e.g., beaucoup de likes pour un nombre de vues standardisé faible, ou l’inverse).
- Un point (views = -1.0, likes = 2.0) signifierait qu’il est 1 écart-type en dessous de la moyenne pour les vues, mais 2 écarts-types au-dessus pour les likes (cas potentiellement anormal, car on n’attend pas tant de likes pour un faible nombre de vues).
""")

# Generate an interative plot with Plotly
fig_interactive = interactive_plot_metrics(data)  
st.plotly_chart(fig_interactive, use_container_width=True)

# ======================================================
# 3. Analyse visuelle : Distribution Interactive des Vues
# ======================================================
st.header("3. Distribution Interactive des Vues")
st.markdown("""
**But :**  
Montre comment les valeurs de views sont réparties sur l’axe (standardisé), et permet de voir où se situe le « cœur » des observations et d’évaluer l’étendue (jusqu’à -1.5, +1.5, etc.).

**Ce que vous voyez :**  
- Un histogramme interactif permettant de zoomer et de survoler.
- Cela offre une vue plus dynamique sur la répartition des vues, facilitant l’identification de valeurs extrêmes ou d’irrégularités.

**Lecture des données :**
- **Axes** :
    - L’axe des x représente les vues (standardisées).
            
    - L'axe des y représente le nombre d'observations dans chaque intervalle (bin).
            
- ** Lecture de Histogramme** :
    - Barres plus hautes : davantage d’observations dans l’intervalle correspondant aux vues.
            
    - Valeur 0 sur l’axe x : moyenne des vues, car elles sont standardisées.
            
    - Valeurs négatives (< 0) : posts ayant moins de vues que la moyenne.
            
    - Valeurs positives (> 0) : posts ayant plus de vues que la moyenne.
            
        
**Conclusion :** 
L’histogramme permet de voir où se situe la majorité des observations (souvent autour du 0 standardisé) :
- S’il y a des barres élevées autour de -1 ou +1, on comprend qu’un pourcentage non négligeable de posts se trouvent avec des vues plus faibles ou plus élevées que la moyenne.
- Les valeurs extrêmes (vers -1.5 ou +1.5, etc.) peuvent indiquer des outliers potentiels, selon la forme de la distribution.
- La visualisation interactive révèle la dispersion des vues et met en évidence des éventuelles anomalies dans la répartition des données.
""")

# Generate an interative histogram with Plotly
fig_distribution = interactive_plot_distribution(data, column='views')
st.plotly_chart(fig_distribution, use_container_width=True)

# ====================================
# 4. Conclusion générale
# ====================================
st.header("Conclusion Générale")
st.markdown("""
**But de l'analyse :**  
L'objectif de ce dashboard est de montrer comment, grâce à une préparation minutieuse des données et à la détection d'anomalies, on peut identifier des incohérences dans des indicateurs tels que les vues et les likes.

**Ce que montrent les visualisations et les statistiques :**  
- L’aperçu du dataset et les statistiques descriptives donnent une vision globale de la qualité et de la répartition des données.
- Le scatter plot permet d’identifier rapidement des observations anormales.
- L’histogramme interactif offre une exploration détaillée de la distribution des vues.

**Conclusion :**  
L'analyse démontre que certaines anomalies existent dans les données, ce qui pourrait indiquer des problèmes dans la collecte ou le traitement des métriques. Ce dashboard illustre une approche complète, depuis le pré-traitement jusqu’à l’interprétation finale, montrant ainsi l’intérêt de l’analyse de données pour prendre des décisions éclairées.
""")

footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        text-align: center;
        padding: 10px 0;
        border-top: 1px solid #ddd;
        font-size: 14px;
        color: gray;
    }
    </style>
    <div class="footer">
        <p>© 2025 GeeksterLab</p>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)
