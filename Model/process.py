import numpy as np
import pickle
from database_connection import fetch_documents_from_mongodb

# Load the Isolation Forest model from a .pkl file
with open('isolation_forest_model_global.pkl', 'rb') as file:
    isolation_forest_model = pickle.load(file)

# Load the LSTM model from a .pkl file
with open('lstm_autoencoder_model_global.pkl', 'rb') as file:
    lstm_model = pickle.load(file)

def calculate_additional_features(data_entry):
    # Calculate acceleration magnitude
    accelX, accelY, accelZ = data_entry['accelX'], data_entry['accelY'], data_entry['accelZ']
    acc_magnitude = np.sqrt(accelX**2 + accelY**2 + accelZ**2)

    # Calculate gyroscope magnitude
    gyroX, gyroY, gyroZ = data_entry['gyroX'], data_entry['gyroY'], data_entry['gyroZ']
    gyro_magnitude = np.sqrt(gyroX**2 + gyroY**2 + gyroZ**2)

    # Example placeholder calculations for jerk and gyro change
    jerk = np.abs(accelX - accelY)  # Example calculation for jerk
    gyro_change = np.abs(gyroX - gyroY)  # Example calculation for gyro change

    # Mean values (you may need historical data or averages based on a window of time)
    acc_magnitude_mean = acc_magnitude  # Placeholder for mean, assuming only one data point
    gyro_magnitude_mean = gyro_magnitude  # Placeholder for mean

    # Speed variation (you may need historical speed data to calculate this)
    speed_variation = 0  # Placeholder value, update based on your data

    # Return all features including the new ones
    return [
        data_entry['accelX'], data_entry['accelY'], data_entry['accelZ'],
        data_entry['gyroX'], data_entry['gyroY'], data_entry['gyroZ'],
        data_entry['speed'], acc_magnitude, gyro_magnitude, jerk,
        gyro_change, acc_magnitude_mean, gyro_magnitude_mean, speed_variation
    ]

def calculate_weights(if_scores, lstm_scores):
    # Calculate the variance of the scores from both models
    if_variance = np.var(if_scores)
    lstm_variance = np.var(lstm_scores)

    # Normalize the variances to get weights
    total_variance = if_variance + lstm_variance
    isolation_forest_weight = if_variance / total_variance
    lstm_weight = lstm_variance / total_variance

    return isolation_forest_weight, lstm_weight

def process_data_entries():
    # Fetch documents from the database
    documents = fetch_documents_from_mongodb()

    if_scores = []
    lstm_scores = []

    # First pass: Collect scores to calculate weights
    for data_entry in documents:
        # Calculate additional features
        features = calculate_additional_features(data_entry)

        # Convert the features into a numpy array for Isolation Forest
        data_array = np.array(features).reshape(1, -1)

        # Get Isolation Forest score
        if_score = isolation_forest_model.decision_function(data_array)[0]
        if_scores.append(if_score)

        # Get LSTM prediction
        lstm_input = np.array(features).reshape((1, 1, len(features)))
        lstm_prediction = lstm_model.predict(lstm_input)[0][0]
        lstm_scores.append(lstm_prediction)

    # Calculate dynamic weights based on the collected scores
    isolation_forest_weight, lstm_weight = calculate_weights(if_scores, lstm_scores)

    results = []

    # Second pass: Use calculated weights for anomaly detection
    for data_entry, if_score, lstm_prediction in zip(documents, if_scores, lstm_scores):
        # Convert Isolation Forest result to binary (1 for anomaly, 0 for normal)
        is_anomaly_if = 1 if isolation_forest_model.predict(np.array([features]))[0] == -1 else 0

        # Calculate weighted anomaly score
        anomaly_score = (isolation_forest_weight * is_anomaly_if) + (lstm_weight * lstm_prediction)
        is_anomaly = anomaly_score > 0.5  # Threshold for anomaly

        # Collect the results
        result = {
            "Data Entry": {k: v for k, v in data_entry.items() if k not in ['_id', '__v', 'latitude', 'longitude']},
            "Isolation Forest Score": if_score,
            "LSTM Prediction": lstm_prediction,
            "Combined Anomaly Score": anomaly_score,
            "Anomaly Detected": is_anomaly
        }
        results.append(result)

    return results

# Example usage
processed_results = process_data_entries()
for result in processed_results:
    print(result)
