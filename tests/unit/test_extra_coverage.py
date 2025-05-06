# tests/unit/test_extra_coverage.py

import os
import runpy
import logging
import pandas as pd
import pytest

# 1) Tests for src/data_preparation.py
from src.data_preparation import get_data, get_clean_data

def test_get_data_save_exception(tmp_path, monkeypatch, capsys):
    # Simulate a DataFrame whose to_csv raises an IOError
    fake = tmp_path / 'fake.csv'
    class BrokenDF(pd.DataFrame):
        def to_csv(self, *args, **kwargs):
            raise IOError("disk error")
    # Monkey-patch simulate_data to return our broken DataFrame

    def fake_simulate_data(n_samples=1000):
        return BrokenDF({'views': [1], 'likes': [2]})

    monkeypatch.setattr('src.data_preparation.simulate_data', fake_simulate_data)

    df = get_data(str(fake), n_samples=1, save_if_generated=True)
    captured = capsys.readouterr()
    # Ensure the save error is printed and we still get a DataFrame back
    assert "Erreur lors de la sauvegarde du dataset" in captured.out
    assert isinstance(df, pd.DataFrame)
    assert not fake.exists()

def test_get_clean_data_save_exception(tmp_path, monkeypatch, capsys):
    # Prepare an existing raw file
    raw = tmp_path / 'raw.csv'
    pd.DataFrame({'views': [1], 'likes': [2]}).to_csv(raw, index=False)
    out_clean = tmp_path / 'clean.csv'

    import src.data_preparation as dp
    # Monkey-patch clean_data to return a DataFrame whose to_csv raises an IOError
    class BrokenDF(pd.DataFrame):
        def to_csv(self, *args, **kwargs):
            raise IOError("write error")
    monkeypatch.setattr(dp, 'clean_data',
                        lambda d: BrokenDF({'views': [1], 'likes': [2]}))

    df = get_clean_data(raw_filepath=str(raw),
                        clean_filepath=str(out_clean),
                        n_samples=1,
                        save_if_generated=True)
    captured = capsys.readouterr()
    # Ensure the clean-save error is printed and we still get a DataFrame back
    assert "Erreur lors de la sauvegarde du dataset nettoyé" in captured.out
    assert isinstance(df, pd.DataFrame)
    assert not out_clean.exists()


# 2) Tests for src/utils.py (success case of setup_logger)

def test_setup_logger_success(tmp_path):
    """
    Verify that setup_logger creates a logger with the given name, level,
    and a FileHandler pointing to the specified file.
    """
    import logging
    from src.utils import setup_logger

    # Prepare a unique logger name and file path
    logger_name = "test_logger_unique"
    log_path = tmp_path / "test.log"

    # Call the real setup_logger (no monkeypatch of getLogger)
    logger = setup_logger(logger_name, str(log_path), level=logging.DEBUG)

    # The returned logger must have the correct name and level
    assert logger.name == logger_name
    assert logger.level == logging.DEBUG

    # Find any FileHandler among its handlers
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    assert file_handlers, "Expected at least one FileHandler on the logger"

    # That handler must write to our log_path
    paths = [h.baseFilename for h in file_handlers]
    assert str(log_path) in paths

    # Cleanup: remove handlers so we don't leak them into other tests
    for h in file_handlers:
        logger.removeHandler(h)
        h.close()


# 3) Tests for src/visualization.py (default save paths)
from src.visualization import plot_distribution, interactive_plot_distribution
import matplotlib.pyplot as plt

def test_plot_distribution_default(tmp_path, monkeypatch, capsys):
    # Change working directory to isolate output
    monkeypatch.chdir(tmp_path)
    # Disable interactive display
    monkeypatch.setattr(plt, 'show', lambda: None)

    df = pd.DataFrame({'views': [5, 10, 15]})
    # Call without specifying save_path
    plot_distribution(df, 'views')
    output_file = tmp_path / 'plots' / 'distribution_views.png'
    # Verify that the file was created and message was printed
    assert output_file.exists()
    assert "Figure saved to" in capsys.readouterr().out

def test_interactive_plot_distribution_default(tmp_path):
    # Change working directory to isolate output
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.chdir(tmp_path)

    df = pd.DataFrame({'views': [1, 2, 3]})
    # Call without specifying output_file
    fig = interactive_plot_distribution(df, column='views')
    html_file = tmp_path / 'plots' / 'distribution_views_interactive.html'
    # Verify that the HTML file was created and fig is a Plotly figure
    assert html_file.exists()
    assert hasattr(fig, 'to_html')

    monkeypatch.undo()


# 4) Tests for src/generate_report.py (PDF generation and header/footer)
from src.generate_report import generate_report, PDF

def test_pdf_header_footer_and_generate_report_with_images(tmp_path, capsys, monkeypatch):
    pdf = PDF()
    pdf.add_page()
    pdf.header()
    pdf.footer()

    metrics_img = tmp_path / 'm.png'; metrics_img.write_bytes(b'')
    dist_img    = tmp_path / 'd.png'; dist_img.write_bytes(b'')

    out_pdf = tmp_path / 'report.pdf'
    # prevent FPDF.image from failing on an invalid PNG
    import src.generate_report as gr
    monkeypatch.setattr(gr.FPDF, 'image', lambda self, name, **kwargs: None)

    result = generate_report(
        total_views=10,
        total_likes=5,
        anomaly_count=1,
        ratio=0.5,
        metrics_image=str(metrics_img),
        distribution_image=str(dist_img),
        metrics_explanation="explanation",
        distribution_explanation="explanation",
        output_file=str(out_pdf)
    )
    # …

    captured = capsys.readouterr()
    # Verify PDF was generated successfully
    assert "Report generated" in captured.out
    assert out_pdf.exists()
    assert result == str(out_pdf)

def test_generate_report_main_block(tmp_path):
    # Re-run the module as a script to hit the bottom asserts in __main__
    import sys
    # ensure a fresh load (so that __main__ block actually runs)
    sys.modules.pop('src.generate_report', None)

    # change cwd so that the report goes into tmp_path
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.chdir(tmp_path)

   # alter_sys=True makes run_module behave like "python -m src.generate_report"
    runpy.run_module('src.generate_report', run_name="__main__", alter_sys=True)

    generated_file = tmp_path / 'report' / 'FakeMetrics_Report.pdf'
    assert generated_file.exists()
    monkeypatch.undo()

# 5) Cover the internal test_handle_missing_data in src/generate_report.py
from src.generate_report import test_handle_missing_data

def test_internal_module_test_handle_missing_data():
    # This will run the module's own test_handle_missing_data()
    # and cover its lines.
    test_handle_missing_data()


# 6) Cover the "image exists" branches of generate_report
import src.generate_report as gr
import pytest

def test_generate_report_with_existing_images(tmp_path, capsys):
    # Create two minimal valid 1×1 PNG files
    png_bytes = (
        b'\x89PNG\r\n\x1a\n'
        b'\x00\x00\x00\rIHDR'
        b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00'
        b'\x90wS\xde'
        b'\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01'
        b'\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    img1 = tmp_path / 'metrics.png'
    img2 = tmp_path / 'dist.png'
    img1.write_bytes(png_bytes)
    img2.write_bytes(png_bytes)

    out_pdf = tmp_path / 'exists_report.pdf'
    # Stub out FPDF.image so it doesn't actually parse the PNG
    monkey = pytest.MonkeyPatch()
    monkey.setattr(gr.FPDF, 'image', lambda self, name, **kwargs: None)

    # Call generate_report with our existing images
    result = gr.generate_report(
        total_views=42,
        total_likes=17,
        anomaly_count=3,
        ratio=17/42,
        metrics_image=str(img1),
        distribution_image=str(img2),
        metrics_explanation="explain",
        distribution_explanation="dist_explain",
        output_file=str(out_pdf)
    )
    out = capsys.readouterr().out

    # Check that the image‐exists path was taken and the report generated
    assert "Report generated" in out
    assert out_pdf.exists()
    assert result == str(out_pdf)

    monkey.undo()