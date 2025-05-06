# src/utils.py

import logging
import pandas as pd

def setup_logger(name, log_file, level=logging.INFO):
    # Configues the logger to record messages in a file

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

def save_to_csv(data: pd.DataFrame, file_path: str) -> bool:
    """
    Sauvegarde un DataFrame dans un fichier CSV.
    
    :param data: DataFrame à sauvegarder
    :param file_path: Chemin du fichier de sortie
    :return: True si la sauvegarde a réussi, False sinon
    """
    try:
        data.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier CSV : {e}")
        return False

def get_column_summary(data: pd.DataFrame, column_name: str) -> dict:
    """
    Renvoie un résumé statistique de la colonne spécifiée.
    
    :param data: DataFrame contenant les données
    :param column_name: Le nom de la colonne dont on veut le résumé
    :return: Un dictionnaire avec les statistiques de base (moyenne, écart-type, min, max)
    """
    summary = {
        'mean': data[column_name].mean(),
        'std': data[column_name].std(),
        'min': data[column_name].min(),
        'max': data[column_name].max()
    }
    return summary



