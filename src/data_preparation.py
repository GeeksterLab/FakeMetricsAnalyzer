# src/data_preparation.py

import pandas as pd
import numpy as np
import os

from sklearn.preprocessing import StandardScaler

# Default file paths
RAW_DATA_PATH = 'data/raw/dataset.csv'
CLEAN_DATA_PATH = 'data/processed/fake_metrics_clean.csv'

# def preprocess_data(data):
#     # Nettoyage des données (par exemple, suppression des valeurs manquantes)
#     data_clean = data.dropna()

#     # Standardisation des caractéristiques
#     data_clean = normalize_features(data_clean)

#     # Ajout de nouvelles fonctionnalités
#     data_clean = add_features(data_clean)

#     return data_clean

def preprocess_data(data):
    # Nettoyage et copie sûre
    data_clean = data.dropna().copy()

    # Standardisation sans warning
    data_clean.loc[:, ['views','likes']] = normalize_features(data_clean)[['views','likes']]

    # Ajout de la feature sans warning
    data_clean.loc[:, 'like_view_ratio'] = data_clean.apply(
        lambda row: row['likes']/row['views'] if row['views']>0 else 0,
        axis=1
    )

    return data_clean

def load_data(filepath):
    # Load data from CSV file

    try :
        data = pd.read_csv(filepath)
        print(f"Dataset chargé depuis : ",filepath)
        return data
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return None

def clean_data(data):
    # Clean the DataFrame : for exemple dropping rows with missings values
    data_clean = data.dropna()

    return data_clean

def simulate_data(n_samples=1000):
    # Generate a simulated dataset with for 'views' and 'likes' metrics
    # Deliberately introduces anomalies (like > views)

    np.random.seed(42)
    views = np.random.randint(50, 1000, n_samples)
    likes = views * np.random.uniform(0.1, 0.9, n_samples)

    # Anomalies introduction: in 5% of the cases : likes > views 
    anomaly_idx = np.random.choice(n_samples, size=int(0.05*n_samples), replace=False)
    likes[anomaly_idx] = views[anomaly_idx] + np.random.randint(1, 50, len(anomaly_idx))

    data = pd.DataFrame({
        'views' : views,
        'likes' : likes.astype(int)
    })
    print("Dataset simulé généré")
    return data

def get_data(filepath, n_samples=1000, save_if_generated=False):
    # Return the raw dataset from a CSV file. If the file does not exist, create a simulated dataset and save it if specified

    if os.path.exists(filepath):
        data = load_data(filepath)
    else:
        data = simulate_data(n_samples=1000)
        if save_if_generated:
            try:
                # Ensure the output directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                data.to_csv(filepath, index=False)
                print("Dataset simulé sauvegardé dans :", filepath)
            except Exception as e:
                print(f"Erreur lors de la sauvegarde du dataset: {e}")
    return data

def get_clean_data(raw_filepath=RAW_DATA_PATH, clean_filepath=CLEAN_DATA_PATH, n_samples=1000, save_if_generated=False):
    # Load the raw dataset, cleand it and save the result in clean_filepath file. If the dataset cleaned already exists, directly load it

    if os.path.exists(clean_filepath):
        data_clean = load_data(clean_filepath)
        print("Clean dataset loaded from :", clean_filepath)
        return data_clean
    else:
        # Load or generate the raw dataset
        data = get_data(raw_filepath, n_samples=500, save_if_generated=True)
        
        # Clean the dataset
        data_clean = clean_data(data)
        if save_if_generated:
            try:
                # Ensure the output directory exists
                os.makedirs(os.path.dirname(clean_filepath), exist_ok=True)
                data_clean.to_csv(clean_filepath, index=False)
                print("Clean dataset saved to :", clean_filepath)
            except Exception as e:
                print(f"Erreur lors de la sauvegarde du dataset nettoyé: {e}")
        return data_clean

def normalize_features(data):
    # Apply to the column 'views' and 'likes' a standardization (Z-score)

    scaler = StandardScaler()
    data[['views', 'likes']] = scaler.fit_transform(data[['views', 'likes']])
    return data

def add_features(data):
    # Add new function to the dataset

    # Calcul the ration likes/views for each observation
    data['like_view_ratio'] = data.apply(lambda row: row["likes"] / row ['views'] if row['views'] > 0 else 0, axis=1)
    return data

def standardize_data(data):
    # Standardisation des colonnes 'views' et 'likes' seulement
    scaler = StandardScaler()
    data[['views', 'likes']] = scaler.fit_transform(data[['views', 'likes']])
    return data


