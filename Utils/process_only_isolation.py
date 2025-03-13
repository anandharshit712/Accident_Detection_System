import json
import numpy as np
import pickle
from datetime import datetime
from bed_allocation.fetch_all_user import fetch_user_data
from bed_allocation.post_json import post_to_mongodb

# Load the Isolation Forest model
with open('../Trained model/isolation_forest_model.pkl', 'rb') as file:
    isolation_forest_model = pickle.load(file)


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


def process_data_and_save_json():
    # Fetch all documents from the database (5 records per user)
    mobile_number_groups = fetch_user_data()

    results = []

    # Process each user's data
    for mobile_number, data_entries in mobile_number_groups.items():
        if len(data_entries) != 5:
            print(f"Mobile Number: {mobile_number} - Accident Detected: False (Insufficient data)")
            continue

        # Calculate additional features using the 5 data points
        features = calculate_additional_features(data_entries)

        # Convert the features into a numpy array for Isolation Forest
        data_array = np.array(features).reshape(1, -1)

        # Use Isolation Forest for anomaly detection
        is_anomaly = isolation_forest_model.predict(data_array).item() == -1

        # Log and save the result if an accident is detected
        print(f"Mobile Number: {mobile_number} - Accident Detected: {is_anomaly}")

        if is_anomaly:
            accident_details = {
                "mobile_number": mobile_number,
                "lat": data_entries[0]['latitude'],
                "long": data_entries[0]['longitude'],
                "status": True
            }
            results.append(accident_details)

    # Save results to a JSON file using the custom DateTimeEncoder
    with open('../accident_status.json', 'w') as j:
        json.dump(results, j, indent=4, cls=DateTimeEncoder)

    return results


# Example usage
processed_results = process_data_and_save_json()

# Post results to MongoDB
post_to_mongodb(processed_results)
print("Data sent to accident database!")
for result in processed_results:
    print(result)
