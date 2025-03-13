import numpy as np
import pickle
from database_connection import fetch_documents_from_mongodb

# Load the Isolation Forest model from a .pkl file
with open('isolation_forest_model_global.pkl', 'rb') as file:
    isolation_forest_model = pickle.load(file)

# Load the LSTM model from a .pkl file
with open('lstm_autoencoder_model.pkl', 'rb') as file:
    lstm_model = pickle.load(file)

def calculate_additional_features(data_entries):
    # Assuming data_entries is a list of the top 10 data points
    accelX_values = [entry['accelX'] for entry in data_entries]
    accelY_values = [entry['accelY'] for entry in data_entries]
    accelZ_values = [entry['accelZ'] for entry in data_entries]
    gyroX_values = [entry['gyroX'] for entry in data_entries]
    gyroY_values = [entry['gyroY'] for entry in data_entries]
    gyroZ_values = [entry['gyroZ'] for entry in data_entries]
    speed_values = [entry['speed'] for entry in data_entries]

    # Use the first data point for individual values
    accelX, accelY, accelZ = accelX_values[0], accelY_values[0], accelZ_values[0]
    gyroX, gyroY, gyroZ = gyroX_values[0], gyroY_values[0], gyroZ_values[0]

    # Calculate acceleration and gyroscope magnitude for the top value
    acc_magnitude = np.sqrt(accelX**2 + accelY**2 + accelZ**2)
    gyro_magnitude = np.sqrt(gyroX**2 + gyroY**2 + gyroZ**2)

    # Calculate mean values over the top 10 data points
    acc_magnitude_mean = np.mean([np.sqrt(x**2 + y**2 + z**2) for x, y, z in zip(accelX_values, accelY_values, accelZ_values)])
    gyro_magnitude_mean = np.mean([np.sqrt(x**2 + y**2 + z**2) for x, y, z in zip(gyroX_values, gyroY_values, gyroZ_values)])

    # Calculate speed variation over the top 10 data points
    speed_variation = np.max(speed_values) - np.min(speed_values)

    # Calculate jerk as the difference between consecutive acceleration values
    jerk = np.mean([
        np.abs(accelX_values[i] - accelX_values[i - 1]) +
        np.abs(accelY_values[i] - accelY_values[i - 1]) +
        np.abs(accelZ_values[i] - accelZ_values[i - 1])
        for i in range(1, len(accelX_values))
    ])

    # Calculate gyro change as the difference between consecutive gyroscope values
    gyro_change = np.mean([
        np.abs(gyroX_values[i] - gyroX_values[i - 1]) +
        np.abs(gyroY_values[i] - gyroY_values[i - 1]) +
        np.abs(gyroZ_values[i] - gyroZ_values[i - 1])
        for i in range(1, len(gyroX_values))
    ])

    # Return all features including the new ones
    return [
        accelX, accelY, accelZ, gyroX, gyroY, gyroZ,
        speed_values[0], acc_magnitude, gyro_magnitude,
        jerk, gyro_change, acc_magnitude_mean,
        gyro_magnitude_mean, speed_variation
    ]

def process_data_entries():
    # Fetch all documents from the database
    documents = fetch_documents_from_mongodb()

    # Group documents by mobile number and take the top 10 data points for each
    mobile_number_groups = {}
    for doc in documents:
        mobile_number = doc['mobileNumber']
        if mobile_number not in mobile_number_groups:
            mobile_number_groups[mobile_number] = []
        mobile_number_groups[mobile_number].append(doc)

    results = []

    # Process each mobile number group
    for mobile_number, data_entries in mobile_number_groups.items():
        # Sort data entries by timestamp in descending order and take the top 10
        data_entries.sort(key=lambda x: x['timestamp'], reverse=True)
        top_10_entries = data_entries[:10]

        # Calculate additional features using the top 10 data points
        features = calculate_additional_features(top_10_entries)

        # Convert the features into a numpy array for Isolation Forest
        data_array = np.array(features).reshape(1, -1)

        # Step 1: Use Isolation Forest for anomaly detection
        is_anomaly_if = 1 if isolation_forest_model.predict(data_array)[0] == -1 else 0

        # Step 2: Prepare the data entry for the LSTM model
        lstm_input = np.array(features).reshape((1, 1, len(features)))
        lstm_prediction = lstm_model.predict(lstm_input)[0][0]

        # Step 3: Calculate weighted anomaly score
        isolation_forest_weight = 0.6  # Adjusted weight
        lstm_weight = 0.4  # Adjusted weight
        anomaly_score = (isolation_forest_weight * is_anomaly_if) + (lstm_weight * lstm_prediction)
        is_anomaly = anomaly_score > 0.5  # Threshold for accident detection

        # Collect the result
        result = {
            "Mobile Number": mobile_number,
            "Accident Detected": is_anomaly
        }
        results.append(result)

    return results

# Example usage
processed_results = process_data_entries()
for result in processed_results:
    print(result)
