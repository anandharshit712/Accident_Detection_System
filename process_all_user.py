import json
import numpy as np
import pickle
from datetime import datetime
from fetch_all_user import fetch_user_data

# Load the Isolation Forest model
with open('isolation_forest_model.pkl', 'rb') as file:
    isolation_forest_model = pickle.load(file)

# Load the LSTM model
with open('lstm_autoencoder_model.pkl', 'rb') as file:
    lstm_model = pickle.load(file)


class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle datetime objects.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string
        return super().default(obj)


def calculate_additional_features(data_entries):
    accelX_values = [entry['accelX'] for entry in data_entries]
    accelY_values = [entry['accelY'] for entry in data_entries]
    accelZ_values = [entry['accelZ'] for entry in data_entries]
    gyroX_values = [entry['gyroX'] for entry in data_entries]
    gyroY_values = [entry['gyroY'] for entry in data_entries]
    gyroZ_values = [entry['gyroZ'] for entry in data_entries]
    speed_values = [entry['speed'] for entry in data_entries]

    accelX, accelY, accelZ = accelX_values[0], accelY_values[0], accelZ_values[0]
    gyroX, gyroY, gyroZ = gyroX_values[0], gyroY_values[0], gyroZ_values[0]

    acc_magnitude = np.sqrt(accelX ** 2 + accelY ** 2 + accelZ ** 2)
    gyro_magnitude = np.sqrt(gyroX ** 2 + gyroY ** 2 + gyroZ ** 2)

    acc_magnitude_mean = np.mean(
        [np.sqrt(x ** 2 + y ** 2 + z ** 2) for x, y, z in zip(accelX_values, accelY_values, accelZ_values)])
    gyro_magnitude_mean = np.mean(
        [np.sqrt(x ** 2 + y ** 2 + z ** 2) for x, y, z in zip(gyroX_values, gyroY_values, gyroZ_values)])

    speed_variation = np.max(speed_values) - np.min(speed_values)

    jerk = np.mean([
        np.abs(accelX_values[i] - accelX_values[i - 1]) +
        np.abs(accelY_values[i] - accelY_values[i - 1]) +
        np.abs(accelZ_values[i] - accelZ_values[i - 1])
        for i in range(1, len(accelX_values))
    ])

    gyro_change = np.mean([
        np.abs(gyroX_values[i] - gyroX_values[i - 1]) +
        np.abs(gyroY_values[i] - gyroY_values[i - 1]) +
        np.abs(gyroZ_values[i] - gyroZ_values[i - 1])
        for i in range(1, len(gyroX_values))
    ])

    return [
        accelX, accelY, accelZ, gyroX, gyroY, gyroZ,
        speed_values[0], acc_magnitude, gyro_magnitude,
        jerk, gyro_change, acc_magnitude_mean,
        gyro_magnitude_mean, speed_variation
    ]


def calculate_dynamic_weights(isolation_forest_score, lstm_score):
    """
    Dynamically calculate weights for the models based on their scores.
    Scores are normalized to sum up to 1.
    """
    total_score = isolation_forest_score + lstm_score
    if total_score == 0:
        return 0.5, 0.5  # Equal weights if both scores are zero
    isolation_forest_weight = isolation_forest_score / total_score
    lstm_weight = lstm_score / total_score
    return isolation_forest_weight, lstm_weight


def normalize_score(score):
    """
    Normalize a score to the range [0, 1] using the sigmoid function.
    """
    return 1 / (1 + np.exp(-score))


def calculate_dynamic_threshold(scores):
    """
    Calculate a dynamic threshold based on the mean of normalized scores.
    """
    if not scores:
        print("Warning: No scores available to calculate the dynamic threshold.")
        return 0  # Default threshold if no scores are available

    # Normalize all scores before calculating the mean
    normalized_scores = [normalize_score(score) for score in scores]
    return np.mean(normalized_scores)


def process_data_and_save_json():
    # Fetch all documents from the database (5 records per user)
    mobile_number_groups = fetch_user_data()

    results = []
    anomaly_scores_map = {}  # Store scores for each user

    # First Pass: Calculate anomaly scores for all users
    for mobile_number, data_entries in mobile_number_groups.items():
        if len(data_entries) != 5:
            print(f"Mobile Number: {mobile_number} - Accident Detected: False (Insufficient data)")
            continue

        # Calculate additional features using the 5 data points
        features = calculate_additional_features(data_entries)

        # Convert the features into a numpy array for Isolation Forest
        data_array = np.array(features).reshape(1, -1)

        # Step 1: Use Isolation Forest for anomaly detection
        isolation_forest_score = 1 if isolation_forest_model.predict(data_array).item() == -1 else 0

        # Step 2: Prepare the data entry for the LSTM model
        lstm_input = np.array(features).reshape((1, 1, len(features)))

        # Debug the LSTM output shape
        lstm_output = lstm_model.predict(lstm_input)  # Predicted reconstruction of the input sequence

        # Original input sequence
        original_sequence = np.squeeze(lstm_input)  # Shape: (10, 14)

        # Reconstructed sequence from the LSTM
        reconstructed_sequence = np.squeeze(lstm_output)  # Shape: (10, 14)

        # Calculate reconstruction error for each time step (Euclidean distance)
        reconstruction_errors = np.sqrt(
            np.sum((original_sequence - reconstructed_sequence) ** 2, axis=1))  # Shape: (10,)

        # Aggregate the errors (mean reconstruction error across all time steps)
        lstm_score = np.mean(reconstruction_errors)

        # Step 3: Calculate dynamic weights
        isolation_forest_weight, lstm_weight = calculate_dynamic_weights(isolation_forest_score, lstm_score)

        # Step 4: Calculate weighted anomaly score
        raw_anomaly_score = (isolation_forest_weight * isolation_forest_score) + (lstm_weight * lstm_score)

        # Normalize the anomaly score to a probability
        anomaly_score = normalize_score(raw_anomaly_score)

        # Store anomaly score for later threshold determination
        anomaly_scores_map[mobile_number] = {
            "score": anomaly_score,
            "latest_data": data_entries[0],  # Keep the most recent data for JSON saving
            "weights": {
                "Isolation Forest Weight": isolation_forest_weight,
                "LSTM Weight": lstm_weight
            }
        }

        # Console log the user's normalized anomaly score
        print(f"Mobile Number: {mobile_number} - Normalized Score: {anomaly_score}")

    # Step 5: Calculate dynamic threshold or use fixed threshold for a single user
    all_scores = [entry["score"] for entry in anomaly_scores_map.values()]
    if len(all_scores) == 1:
        print("Single user detected. Using a fixed threshold of 0.5.")
        dynamic_threshold = 0.5  # Fixed threshold for single user
    else:
        dynamic_threshold = calculate_dynamic_threshold(all_scores)  # Dynamic threshold for multiple users

    print(f"Dynamic Threshold: {dynamic_threshold}")

    # Second Pass: Save results for anomalies and log the status for all users
    for mobile_number, data in anomaly_scores_map.items():
        anomaly_score = data["score"]
        is_anomaly = anomaly_score > dynamic_threshold  # Compare score with the threshold

        # Console log the status for all users
        print(f"Mobile Number: {mobile_number} - Accident Detected: {is_anomaly}")

        if is_anomaly:  # Save only true anomalies
            accident_details = {
                "Mobile Number": mobile_number,
                "Timestamp": data["latest_data"]['timestamp'],
                "Location": {
                    "Latitude": data["latest_data"]['latitude'],
                    "Longitude": data["latest_data"]['longitude']
                },
                "Accident Detected": True,
                "Weights": data["weights"]
            }
            results.append(accident_details)

    # Save results to a JSON file using the custom DateTimeEncoder
    with open('accident_status.json', 'w') as j:
        json.dump(results, j, indent=4, cls=DateTimeEncoder)

    return results


# Example usage
processed_results = process_data_and_save_json()
for result in processed_results:
    print(result)
