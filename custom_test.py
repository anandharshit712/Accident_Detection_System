import numpy as np
import pickle
from pymongo import MongoClient

# MongoDB Atlas Connection
client = MongoClient("mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb")  # Replace with your MongoDB Atlas connection string
db = client["test"]  # Replace with your database name
collection = db["accidents"]  # Replace with your collection name

# Load the trained Isolation Forest model
with open('Trained model/isolation_forest_model.pkl', 'rb') as file:
    isolation_forest_model = pickle.load(file)


def calculate_additional_features(data_entries):
    """
    Calculate derived features like magnitude, jerk, etc.
    """
    accelX_values = [entry['accelX'] for entry in data_entries]
    accelY_values = [entry['accelY'] for entry in data_entries]
    accelZ_values = [entry['accelZ'] for entry in data_entries]
    gyroX_values = [entry['gyroX'] for entry in data_entries]
    gyroY_values = [entry['gyroY'] for entry in data_entries]
    gyroZ_values = [entry['gyroZ'] for entry in data_entries]
    speed_values = [entry['speed'] for entry in data_entries]

    acc_magnitude = np.sqrt(accelX_values[0] ** 2 + accelY_values[0] ** 2 + accelZ_values[0] ** 2)
    gyro_magnitude = np.sqrt(gyroX_values[0] ** 2 + gyroY_values[0] ** 2 + gyroZ_values[0] ** 2)

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

    acc_magnitude_mean = np.mean(
        [np.sqrt(x ** 2 + y ** 2 + z ** 2) for x, y, z in zip(accelX_values, accelY_values, accelZ_values)])
    gyro_magnitude_mean = np.mean(
        [np.sqrt(x ** 2 + y ** 2 + z ** 2) for x, y, z in zip(gyroX_values, gyroY_values, gyroZ_values)])
    speed_variation = np.max(speed_values) - np.min(speed_values)

    return [
        accelX_values[0], accelY_values[0], accelZ_values[0],
        gyroX_values[0], gyroY_values[0], gyroZ_values[0],
        speed_values[0], acc_magnitude, gyro_magnitude,
        jerk, gyro_change, acc_magnitude_mean, gyro_magnitude_mean, speed_variation
    ]


def predict_accident_status(custom_data):
    """
    Predict accident status for the given custom data using the Isolation Forest model.
    """
    # Validate input data
    if len(custom_data) != 5:
        raise ValueError("Custom data must contain exactly 5 data points for consistent feature calculation.")

    # Calculate features
    features = calculate_additional_features(custom_data)
    features_array = np.array(features).reshape(1, -1)

    # Predict using Isolation Forest
    is_anomaly = isolation_forest_model.predict(features_array).item() == -1

    # Output prediction result
    # status = "true" if is_anomaly else "false"
    return {
        "status": True,
        "features": features,
        "is_anomaly": is_anomaly
    }


def send_to_mongodb(result, custom_data):
    """
    Send the accident status to MongoDB if an accident is detected.
    """
    if result["is_anomaly"]:
        # Convert numpy types to Python native types
        python_features = [float(x) for x in result["features"]]  # Ensure all features are Python floats

        # Create a document with the required fields
        document = {
            "mobile_number": "1234567890",  # Example mobile number
            "lat": float(custom_data[0].get("latitude")),  # Convert latitude to Python float
            "long": float(custom_data[0].get("longitude")),  # Convert longitude to Python float
            "status": result["status"],
        }

        # Insert into MongoDB
        collection.insert_one(document)
        print("Accident status sent to MongoDB Atlas!")
    else:
        print("No accident detected. Data not sent to MongoDB.")


# Example Usage
if __name__ == "__main__":
    # Custom data provided by the user
    custom_data = [
        {"accelX": 15.0, "accelY": 8.0, "accelZ": 10.0, "gyroX": 5.0, "gyroY": 7.0, "gyroZ": 6.0, "speed": 60, "latitude": 12.9716, "longitude": 77.5946},
        {"accelX": 14.0, "accelY": 7.5, "accelZ": 9.5, "gyroX": 4.5, "gyroY": 6.8, "gyroZ": 5.8, "speed": 62, "latitude": 12.9717, "longitude": 77.5947},
        {"accelX": 16.0, "accelY": 8.5, "accelZ": 10.5, "gyroX": 5.2, "gyroY": 7.2, "gyroZ": 6.2, "speed": 55, "latitude": 12.9718, "longitude": 77.5948},
        {"accelX": 13.5, "accelY": 7.0, "accelZ": 9.0, "gyroX": 4.8, "gyroY": 6.5, "gyroZ": 5.5, "speed": 58, "latitude": 12.9719, "longitude": 77.5949},
        {"accelX": 15.5, "accelY": 8.2, "accelZ": 10.2, "gyroX": 5.1, "gyroY": 7.1, "gyroZ": 6.1, "speed": 50, "latitude": 12.9720, "longitude": 77.5950},
    ]

    # Predict accident status
    result = predict_accident_status(custom_data)
    print("Prediction Result:", result)

    # Send to MongoDB if accident is detected
    send_to_mongodb(result, custom_data)
