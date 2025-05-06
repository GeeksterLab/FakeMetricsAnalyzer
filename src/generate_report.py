# src/generate_report.py

from fpdf import FPDF

import pandas as pd
import os 

metrics_image: str = 'plots/metrics_scatter.png'  # Annoncer explicitement le type comme str
distribution_image: str = 'plots/distribution_views.png'  # Annoncer explicitement le type comme str
metrics_explanation: str = 'plots/metrics_explanation.png'  # Annoncer explicitement le type comme str
anomaly_count: int = 20  # Annoncer explicitement le type comme int

class PDF(FPDF):
    def header(self):
        # Header
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Fake Metrics Report', ln=True, align='C')
        self.ln(10)

    def footer(self):
        # Footer
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}  © 2025 GeeksterLab', 0, 0, 'C')

def generate_report(total_views, total_likes, anomaly_count, ratio, 
                    metrics_image, distribution_image, metrics_explanation, 
                    distribution_explanation, output_file='report/FakeMetrics_Report.pdf'):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Informations globales
    pdf.cell(0, 10, f"Total Views: {total_views}", ln=True)
    pdf.cell(0, 10, f"Total Likes: {total_likes}", ln=True)
    pdf.cell(0, 10, f"Number of Anomalies Detected: {anomaly_count}", ln=True)
    pdf.cell(0, 10, f"Ratio (likes/views): {ratio:.2f}", ln=True)
    pdf.ln(10)

    # Ajout de l'image du scatter plot
    pdf.cell(0, 10, "Scatter Plot of Views vs Likes (with anomalies):", ln=True)
    if os.path.exists(metrics_image):
        pdf.image(metrics_image, w=pdf.w - 20)
    else:
        pdf.cell(0, 10, f"[Image non trouvée: {metrics_image}]", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, metrics_explanation)
    pdf.ln(10)

    # Ajout de l'image de distribution
    pdf.cell(0, 10, "Distribution of Views:", ln=True)
    if os.path.exists(distribution_image):
        pdf.image(distribution_image, w=pdf.w - 20)
    else:
        pdf.cell(0, 10, f"[Image non trouvée: {distribution_image}]", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, distribution_explanation)

    # Ensure the output directory exists (if any)
    dirpath = os.path.dirname(output_file)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    # Sauvegarder le rapport en PDF
    try:
        pdf.output(output_file)
        print(f"Report generated: {output_file}")
        return output_file  # Retourner le chemin du fichier généré
    except Exception as e:
        print(f"[ERROR] Erreur lors de la génération du rapport: {e}")  # Débogage
        return None  # Retourner None en cas d'erreur


if __name__ == "__main__":
    total_views = 1000
    total_likes = 300
    anomaly_count = 20
    ratio = total_likes / total_views
    
    metrics_explanation = (
        "Ici, on explique la signification du scatter plot : chaque point représente un post,\n"
        "avec le nombre de vues en abscisse et le nombre de likes en ordonnée.\n"
        "Les points en rouge indiquent des anomalies détectées."
    )
    distribution_explanation = (
        "Ici, on décrit l'histogramme des vues.\n"
        "Cela permet de voir si certaines tranches de vues sont sur- ou sous-représentées."
    )
    
    # Call the method to generate the report
    report = generate_report(
        total_views,
        total_likes,
        anomaly_count,
        ratio,
        metrics_image,
        distribution_image,
        metrics_explanation,
        distribution_explanation
    )
    assert report is not None, "Le rapport n'a pas été généré."  # Vérifie que le chemin du rapport est retourné
    assert os.path.exists(report), "Le fichier de rapport n'existe pas."  # Vérifie que le fichier existe réellement

def handle_missing_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Gère les données manquantes dans le DataFrame en les supprimant.
    Peut être étendu pour effectuer des imputs ou d'autres traitements sur les valeurs manquantes.
    
    :param data: DataFrame à traiter
    :return: DataFrame avec les valeurs manquantes gérées
    """
    # Suppression des lignes avec des valeurs manquantes
    return data.dropna()  # Tu peux aussi utiliser imputation si nécessaire


def test_handle_missing_data():
    data = pd.DataFrame({'views': [100, None], 'likes': [10, 20]})
    result = handle_missing_data(data)
    assert result.isnull().sum().sum() == 0


