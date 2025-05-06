# app.py

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os

from streamlit_lottie import st_lottie
from src.data_preparation import get_clean_data, add_features, normalize_features
from src.anomaly_detection import detect_anomalies, detect_anomalies_lof
from src.visualization import interactive_plot_distribution, interactive_plot_metrics


# -- Page config ---------------------------------------
st.set_page_config("Fake Metrics Dashboard", "📊", layout="wide")

# -- Optional: Lottie animation ------------------------
def load_lottie(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

lottie = load_lottie("https://assets5.lottiefiles.com/packages/lf20_touohxv0.json")
if lottie:
    st_lottie(lottie, height=150)

# -- Custom CSS ----------------------------------------
st.markdown("""
<style>
h1, h2, h3 { color: #2a9d8f; }
.stButton>button { background-color: #e76f51; color: white; border-radius:4px; }
</style>
""", unsafe_allow_html=True)


# ====================================
# 🛈 How It Works
# ====================================
with st.sidebar.expander("ℹ️ How to interact with this dashboard", expanded=True):
    st.markdown("""
    **1) Interactive Tables**  
    - You can **sort** columns by clicking on their headers.  
    - Use the **search box** (top-right) to filter rows.  

    **2) Scatter Plot**  
    - **Hover** on a point to see its exact `(views, likes, anomaly)` values.  
    - **Drag** to zoom into a region.  
    - **Double-click** to reset the view.  
    - Use the **lasso** or **box select** tools in the top-right menu to select subsets of points.  

    **3) Histogram**  
    - **Hover** over a bar to see count & bin range.  
    - **Drag** to zoom in on frequency ranges.  
    - **Double-click** to reset.  
    """)


st.title("Fake Metrics Dashboard")

st.markdown("""
- **Fake Metrics Analyzer** is a Python project designed to analyze fake metrics like views and likes on posts to detect anomalies. 
- The project generates detailed reports, provides visualizations (such as a scatter plot of views vs likes), and allows exploration of anomalies and trends in the data.
""")

st.header("1. Data Loading & Preparation")
st.markdown("""
**Goal:**  
Load the dataset, generate new features, and normalize values for consistent analysis.

**What you’ll see:**  
- A preview of the first few rows of the dataset.  
- Descriptive statistics to understand the data distribution.  

- Anomaly detection identifying points that deviate significantly from the general trend.  
- Data normalization to facilitate comparison across metrics.
""")

# Load and prepare the dataset
data = get_clean_data(n_samples=500, save_if_generated=True)
data = add_features(data)
data = normalize_features(data)
data = detect_anomalies(data, contamination=0.05)

# Display an overview of the dataset
st.write("### Dataset Preview", data.head())
st.markdown("""
**Dataset description:**  
- **views**: Number of video views (standardized).  
- **likes**: Number of video likes (standardized).  
- **like-view-ratio**: Raw likes/views ratio.  
- **anomaly**: Binary flag (0 = normal, 1 = anomaly).

**How to read:**  
- **views & likes** are standardized, so their means are near 0.  
  - A negative value (e.g. -1.356) is that many standard deviations below the mean.  
  - A positive value (e.g. +1.387) is above the mean.  
- **like-view-ratio** is computed on the raw data. A ratio of 0.63 means ~63% likes per view.  
  - A ratio > 1 indicates more likes than views—often considered anomalous.  
- **anomaly** is produced by our detection algorithm (Isolation Forest).  
  - 0 = considered normal  
  - 1 = flagged as anomaly (e.g. more likes than views)

**Conclusion:**  
In the preview above, all `anomaly` values are 0, meaning these observations are considered normal.
""")

st.write("### Descriptive Statistics", data.describe())
st.markdown("""
**Statistics breakdown:**  
- **count:** Total number of observations.  
- **mean:**  
  - views ≈ 0.00, likes ≈ 0.00 (post-standardization).  
  - like-view-ratio ≈ 0.52 (on raw data).  
  - anomaly ≈ 0.05 (≈5% flagged).  
- **std:**  
  - views & likes ≈ 1.00 (standardization works).  
  - like-view-ratio ≈ 0.26 (spread around 0.52).  
  - anomaly ≈ 0.22 (binary dispersion).  
- **min / max / percentiles:**  
  Shows the range and quartiles for each metric.
""")

# ====================================
# 2. Interactive Scatter Plot
# ====================================
st.header("2. Interactive Scatter Plot: Views vs. Likes")
st.markdown("""
**Goal:**  
Highlight the relationship between views and likes and spot anomalies visually.

**What you’ll see:**  
- A scatter plot of each point by views (x) and likes (y).  
- Color differentiates Normal vs. Anomaly.

**How to read:**  
- **X-axis (views):** Negative = below average, positive = above average.  
- **Y-axis (likes):** Same interpretation for likes.  
- **Color:**  
  - Blue = Normal  
  - Red = Anomaly (points flagged as unusual by the algorithm)

**Conclusion:**  
Anomalous points stand out in red, indicating potential data issues (e.g. more likes than views).
""")

fig_interactive = interactive_plot_metrics(data)
st.plotly_chart(fig_interactive, use_container_width=True, key="interactive_scatter")

# ====================================
# 3. Interactive Histogram: Views
# ====================================
st.header("3. Interactive Distribution of Views")
st.markdown("""
**Goal:**  
Show how views are distributed and allow dynamic exploration of data spread.

**What you’ll see:**  
- An interactive histogram with zoom and hover capabilities.

**How to read:**  
- **X-axis:** Standardized views.  
- **Y-axis:** Count of observations in each bin.

**Conclusion:**  
This helps identify where most observations lie (usually around 0) and spot any extreme values.
""")

fig_distribution = interactive_plot_distribution(data, column='views')
st.plotly_chart(fig_distribution,   use_container_width=True, key="interactive_hist")

# ====================================
# 4. Overall Conclusion
# ====================================
st.header("4. Overall Conclusion")
st.markdown("""
This dashboard demonstrates how thorough data preparation and anomaly detection can uncover inconsistencies in metrics like views and likes.

- **Data preview & stats** give you a global picture of distribution and quality.  
- **Scatter plot** quickly highlights anomalous points.  
- **Interactive histogram** offers detailed insight into view distribution.

Anomalies flagged by the model may indicate issues in data collection or processing, underscoring the value of this analysis for informed decision-making.
""")

# Footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f9f9f9;
        text-align: center;
        padding: 8px 0;
        border-top: 1px solid #ddd;
        font-size: 12px;
        color: #666;
    }
    </style>
    <div class="footer">
        © 2025 GeeksterLab
    </div>
    """,
    unsafe_allow_html=True
)

