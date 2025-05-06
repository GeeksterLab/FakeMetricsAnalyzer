# tests/integration/test_main_pipeline.py

import pytest
import sys
import runpy

import main as main_module

@pytest.mark.integration
def test_main_generates_all_outputs(tmp_path, monkeypatch):
    # 1) isole le cwd
    monkeypatch.chdir(tmp_path)

    # 2) stubber pour ne pas ouvrir de vraies fenêtres
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda *args, **kwargs: None)

    # 3) stubber pour FPDF.image (éviter les erreurs PNG)
    import src.generate_report as gr
    monkeypatch.setattr(gr.FPDF, 'image', lambda self, name, **kwargs: None)

    # 4) Exécute main()
    main_module.main()

    # 5) Vérifie que les dossiers et fichiers attendus ont bien été créés
    assert (tmp_path / 'plots' / 'metrics_scatter.png').exists()
    assert (tmp_path / 'plots' / 'distribution_views.png').exists()
    assert (tmp_path / 'plots' / 'metrics_scatter_interactive.html').exists()
    assert (tmp_path / 'plots' / 'distribution_views_interactive.html').exists()
    assert (tmp_path / 'FakeMetrics_Report.pdf').exists()

@pytest.mark.integration
def test_main_entry_point_runs_main(tmp_path, monkeypatch):
    """
    Execute main.py as a script (so that the
    `if __name__ == '__main__': main()` branch is covered).
    """
    # 1) Isole le cwd
    monkeypatch.chdir(tmp_path)

    # 2) Stub les affichages et PDF.image
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda *args, **kwargs: None)
    import src.generate_report as gr
    monkeypatch.setattr(gr.FPDF, 'image', lambda self, name, **kwargs: None)

    # 3) Vide le module pour forcer la ré-exécution
    sys.modules.pop('main', None)

    # 4) Lance main.py comme un script
    runpy.run_module('main', run_name="__main__", alter_sys=True)

    # 5) Vérifie que le rapport a bien été généré
    assert (tmp_path / 'FakeMetrics_Report.pdf').exists()