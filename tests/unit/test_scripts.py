# tests/unit/test_scripts.py

import pytest
import pandas as pd
import numpy as np
import src.utils

from src.anomaly_detection import detect_anomalies, detect_anomalies_lof
from src.data_preparation import (
    preprocess_data, load_data, clean_data, simulate_data,
    get_data, get_clean_data, normalize_features, add_features, standardize_data
)
from src.generate_report import generate_report, handle_missing_data
from src.visualization import (
    plot_metrics, plot_distribution,
    interactive_plot_metrics, interactive_plot_distribution
)

def test_detect_anomalies_columns_and_output(capsys):
    df = pd.DataFrame({'views': [10, 20, 30], 'likes': [1, 2, 3]})
    result = detect_anomalies(df.copy(), contamination=0.1)
    assert 'anomaly' in result.columns
    assert result['anomaly'].isin([0, 1]).all()
    captured = capsys.readouterr()
    assert "Number of anomalies detected" in captured.out

def test_detect_anomalies_lof_mapping():
    df = pd.DataFrame({'views': [10, 20, 30], 'likes': [1, 2, 3]})
    result = detect_anomalies_lof(df.copy(), n_neighbors=2, contamination=0.1)
    assert 'anomaly_lof' in result.columns
    assert result['anomaly_lof'].isin([0, 1]).all()

def test_clean_data_drops_missing():
    df = pd.DataFrame({'views': [1, None], 'likes': [10, 20]})
    clean = clean_data(df)
    assert clean.isnull().sum().sum() == 0

def test_normalize_and_standardize_behavior():
    df = pd.DataFrame({'views': [1,2,3], 'likes': [2,4,6]})
    norm = normalize_features(df.copy())

    # mean ≃ 0
    assert abs(norm['views'].mean()) < 1e-6
    # std population ≃ 1
    assert abs(norm['views'].std(ddof=0) - 1) < 1e-6

    std = standardize_data(df.copy())
    assert abs(std['likes'].mean()) < 1e-6

def test_add_features_ratios_and_zero_division():
    df = pd.DataFrame({'views': [0, 2], 'likes': [5, 4]})
    out = add_features(df.copy())
    assert out.loc[0, 'like_view_ratio'] == 0
    assert out.loc[1, 'like_view_ratio'] == 4 / 2

def test_preprocess_data_pipeline(tmp_path):
    df = pd.DataFrame({'views': [1, None, 2], 'likes': [4, 5, 6]})
    processed = preprocess_data(df.copy())
    assert 'like_view_ratio' in processed.columns
    assert processed.isnull().sum().sum() == 0

def test_load_data_success_and_failure(tmp_path, capsys):
    # Success
    file = tmp_path / 'test.csv'
    df = pd.DataFrame({'a': [1, 2]})
    df.to_csv(file, index=False)
    data = load_data(str(file))
    captured = capsys.readouterr()
    assert "Dataset chargé depuis" in captured.out
    pd.testing.assert_frame_equal(data, df)

    # Failure
    data_none = load_data(str(tmp_path / 'no.csv'))
    captured = capsys.readouterr()
    assert data_none is None
    assert "Erreur lors du chargement des données" in captured.out

def test_simulate_data_and_print(capsys):
    df = simulate_data(50)
    assert isinstance(df, pd.DataFrame)
    assert 'views' in df.columns and 'likes' in df.columns
    captured = capsys.readouterr()
    assert "Dataset simulé généré" in captured.out

def test_get_data_branches(tmp_path):
    # File exists
    file = tmp_path / 'exists.csv'
    df = pd.DataFrame({'views': [1], 'likes': [2]})
    df.to_csv(file, index=False)
    data1 = get_data(str(file), n_samples=10, save_if_generated=True)
    pd.testing.assert_frame_equal(data1, df)

    # File does not exist, save
    file2 = tmp_path / 'new.csv'
    data2 = get_data(str(file2), n_samples=10, save_if_generated=True)
    assert isinstance(data2, pd.DataFrame)
    assert file2.exists()

    # File does not exist, no save
    file3 = tmp_path / 'nosave.csv'
    data3 = get_data(str(file3), n_samples=5, save_if_generated=False)
    assert isinstance(data3, pd.DataFrame)
    assert not file3.exists()

def test_get_clean_data_branches(tmp_path, capsys):
    # Clean file exists
    clean = tmp_path / 'clean.csv'
    df = pd.DataFrame({'views': [1], 'likes': [2]})
    df.to_csv(clean, index=False)
    loaded = get_clean_data(clean_filepath=str(clean))
    captured = capsys.readouterr()
    assert "Clean dataset loaded from" in captured.out
    pd.testing.assert_frame_equal(loaded, df)

    # Clean file does not exist
    raw = tmp_path / 'raw.csv'
    raw_df = pd.DataFrame({'views': [1, None], 'likes': [2, 3]})
    raw_df.to_csv(raw, index=False)
    out_clean = tmp_path / 'out_clean.csv'
    result = get_clean_data(raw_filepath=str(raw), clean_filepath=str(out_clean), n_samples=5, save_if_generated=True)
    assert isinstance(result, pd.DataFrame)
    assert out_clean.exists()

def test_handle_missing_data_function():
    df = pd.DataFrame({'x': [1, None], 'y': [2, 3]})
    cleaned = handle_missing_data(df)
    assert cleaned.isnull().sum().sum() == 0

def test_generate_report_success_and_error(tmp_path, monkeypatch, capsys):
    # Success path
    out_file = tmp_path / 'report.pdf'
    result = generate_report(10, 5, 2, 0.5,
                             'no_metrics.png', 'no_dist.png',
                             'explain', 'dist_explain',
                             output_file=str(out_file))
    captured = capsys.readouterr()
    assert result == str(out_file)
    assert "Report generated" in captured.out
    assert out_file.exists()

    # Error path: simulate FPDF.output failing
    import src.generate_report as gr
    monkeypatch.setattr(gr.FPDF, 'output', lambda self, path: (_ for _ in ()).throw(Exception("fail")))
    err = generate_report(1, 1, 0, 1.0, 'x', 'y', 'e', 'd', output_file=str(tmp_path / 'err.pdf'))
    captured = capsys.readouterr()
    assert err is None
    assert "[ERROR] Erreur lors de la génération du rapport" in captured.out


# def test_setup_logger_raises_attribute_error():
#     import logging
#     with pytest.raises(AttributeError):
#         src.utils.setup_logger('test', 'test.log', level=logging.INFO)


def test_save_to_csv_success_and_failure(tmp_path, monkeypatch):
    # Success
    df = pd.DataFrame({'a': [1]})
    file = tmp_path / 'out.csv'
    assert src.utils.save_to_csv(df, str(file))
    assert file.exists()

    # Failure: monkeypatch to_csv
    class DummyDF:
        def to_csv(self, path, index=False):
            raise Exception("fail")
    dummy = DummyDF()
    assert src.utils.save_to_csv(dummy, 'any.csv') is False


def test_get_column_summary_values():
    df = pd.DataFrame({'a': [1, 2, 3, 4]})
    summary = src.utils.get_column_summary(df, 'a')
    assert summary['mean'] == 2.5
    assert summary['std'] == df['a'].std()
    assert summary['min'] == 1
    assert summary['max'] == 4


def test_plot_metrics_and_distribution_and_interactive(tmp_path, monkeypatch, capsys):
    # Prepare data
    df = pd.DataFrame({'views': [1, 2], 'likes': [2, 3], 'anomaly': [0, 1]})
    save_metrics = tmp_path / 'metrics.png'
    save_dist = tmp_path / 'dist.png'

    # Prevent actual display
    monkeypatch.setattr(plot_metrics.__globals__['plt'], 'show', lambda: None)

    plot_metrics(df, save_path=str(save_metrics))
    out = capsys.readouterr()
    assert str(save_metrics) in out.out
    assert save_metrics.exists()

    plot_distribution(df, 'views', save_path=str(save_dist))
    out = capsys.readouterr()
    assert str(save_dist) in out.out
    assert save_dist.exists()

    # Interactive metrics
    int_metrics = tmp_path / 'int_metrics.html'
    fig1 = interactive_plot_metrics(df, output_file=str(int_metrics))
    out = capsys.readouterr()
    assert str(int_metrics) in out.out
    assert int_metrics.exists()
    assert hasattr(fig1, 'to_html')

    # Without anomaly column
    df2 = pd.DataFrame({'views': [1], 'likes': [2]})
    int_metrics2 = tmp_path / 'int2.html'
    fig2 = interactive_plot_metrics(df2, output_file=str(int_metrics2))
    out = capsys.readouterr()
    assert "Warning: the 'anomaly' column is not present; all points will be marked 'Normal'." in out.out
    assert int_metrics2.exists()
    assert hasattr(fig2, 'to_html')

    # Interactive distribution
    int_dist = tmp_path / 'int_dist.html'
    fig3 = interactive_plot_distribution(df, column='views', output_file=str(int_dist))
    out = capsys.readouterr()
    assert str(int_dist) in out.out
    assert int_dist.exists()
    assert hasattr(fig3, 'to_html')
