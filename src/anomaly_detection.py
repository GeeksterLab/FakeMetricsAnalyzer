# src/anomaly_detection.py

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

def detect_anomalies(data, contamination=0.05):
    # Uses IsolationForest to detect anomalies in the 'views 'and 'likes' columns

    # param data: DataFrame containing the metrics.
    # :param contamination: The expected ratio of anomalies.
    # :return: DataFrame with an 'anomaly' column (1 for an anomaly, 0 for normal)
    features = data[['views', 'likes']]

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(features)

    # Prediction : -1 for an anomaly, 1 indicate normal
    # Convert -1 to 1 (anomaly) and 1 to 0 (normal)
    data['anomaly'] = model.predict(features)
    data['anomaly'] = data['anomaly'].apply(lambda x: 1 if x == -1 else 0)

    # Number of anomalies detected
    anomaly_count = data['anomaly'].sum()
    print(f"Number of anomalies detected: {anomaly_count}")

    return data

def detect_anomalies_lof(data, n_neighbors=20, contamination=0.05):
    # Detect anomalies using Local Outlier Factor
    # Add a column 'anomaly_lof' where 1 indicates an anomaly

    features = data[['views', 'likes']]
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
    data['anomaly_lof'] = lof.fit_predict(features)

    # Mapping : -1 (anomalie) transform to 1 et 1 (normal) transform to 0
    data['anomaly_lof'] = data['anomaly_lof'].apply(lambda x: 1 if x == -1 else 0)
    return data

    #