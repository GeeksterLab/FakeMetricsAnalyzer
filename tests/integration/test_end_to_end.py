# tests/integration/test_end_to_end.py

import os
import pandas as pd
import pytest

# 1) Data prep
from src.data_preparation import simulate_data, preprocess_data
# 2) Anomaly detection
from src.anomaly_detection import detect_anomalies, detect_anomalies_lof
# 3) Visualization (static)
from src.visualization import plot_metrics, plot_distribution
# 4) Report generation
from src.generate_report import generate_report

@pytest.mark.integration
def test_end_to_end_pipeline(tmp_path, monkeypatch):
    """
    Runs a full pipeline:
      1. simulate data
      2. preprocess
      3. detect anomalies (IsolationForest + LOF)
      4. plot metrics & distribution (to files)
      5. generate PDF report
    Verifies that each step produces the expected outputs.
    """

    # --- isolate outputs in tmp_path ---
    monkeypatch.chdir(tmp_path)

    # --- disable interactive displays ---
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)

    # --- prevent PDF.image from parsing real PNGs ---
    import src.generate_report as gr
    monkeypatch.setattr(gr.FPDF, 'image', lambda self, name, **kwargs: None)

    # 1) Simulate raw data
    df = simulate_data(n_samples=100)
    assert not df.empty
    assert set(df.columns) == {'views', 'likes'}

    # 2) Preprocess (dropna, normalize, add ratio)
    df_clean = preprocess_data(df)
    assert 'like_view_ratio' in df_clean.columns
    # no missing values
    assert df_clean.isnull().sum().sum() == 0

    # 3) Detect anomalies
    df_anom = detect_anomalies(df_clean.copy(), contamination=0.05)
    df_anom = detect_anomalies_lof(df_anom.copy(), n_neighbors=5, contamination=0.05)
    # both columns should be present
    assert 'anomaly' in df_anom.columns
    assert 'anomaly_lof' in df_anom.columns

    # 4) Produce static plots
    metrics_img = tmp_path / 'metrics_scatter.png'
    dist_img    = tmp_path / 'distribution_views.png'
    plot_metrics(df_anom, save_path=str(metrics_img))
    plot_distribution(df_anom, 'views', save_path=str(dist_img))
    assert metrics_img.exists()
    assert dist_img.exists()

    # 5) Generate PDF report
    total_views   = int(df_anom['views'].sum())
    total_likes   = int(df_anom['likes'].sum())
    anomaly_count = int(df_anom['anomaly'].sum())
    ratio         = total_likes / total_views if total_views else 0
    out_pdf = tmp_path / 'Final_Report.pdf'

    result = generate_report(
        total_views=total_views,
        total_likes=total_likes,
        anomaly_count=anomaly_count,
        ratio=ratio,
        metrics_image=str(metrics_img),
        distribution_image=str(dist_img),
        metrics_explanation="Here is the metrics scatter plot.",
        distribution_explanation="Here is the views distribution.",
        output_file=str(out_pdf)
    )

    # The PDF should have been created and returned
    assert out_pdf.exists()
    assert result == str(out_pdf)
