import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import pickle

# Load datasets
training_data = pd.read_csv("../Detection_model_mobile/gps_dataset/dataset_training/data_set_training.csv")
controlled_test_data = pd.read_csv(
    "../Detection_model_mobile/gps_dataset/dataset_controlled_test/data_set_controlled_test.csv")
phones_gyroscope_data = pd.read_csv("../Detection_model_mobile/Phones_gyroscope_reduced/Phones_gyroscope1.csv")
phones_accelerometer_data = pd.read_csv(
    "../Detection_model_mobile/Phones_accelerometer_reduced/Phones_accelerometer1.csv")

# Rename columns in the Phones datasets to match expected feature names
phones_gyroscope_data = phones_gyroscope_data.rename(columns={'x': 'gyrox', 'y': 'gyroy', 'z': 'gyroz'})
phones_accelerometer_data = phones_accelerometer_data.rename(columns={'x': 'accx', 'y': 'accy', 'z': 'accz'})

# Add dummy columns for missing fields (assuming speed is missing)
for col in ['speed', 'accx', 'accy', 'accz']:
    if col not in phones_gyroscope_data:
        phones_gyroscope_data[col] = np.nan

for col in ['speed', 'gyrox', 'gyroy', 'gyroz']:
    if col not in phones_accelerometer_data:
        phones_accelerometer_data[col] = np.nan

# Feature Engineering Function
def add_enhanced_features(df):
    df['acc_magnitude'] = np.sqrt(df['accx'] ** 2 + df['accy'] ** 2 + df['accz'] ** 2)
    df['gyro_magnitude'] = np.sqrt(df['gyrox'] ** 2 + df['gyroy'] ** 2 + df['gyroz'] ** 2)
    df['jerk'] = df[['accx', 'accy', 'accz']].diff().pow(2).sum(axis=1).pow(0.5)
    df['gyro_change'] = df[['gyrox', 'gyroy', 'gyroz']].diff().pow(2).sum(axis=1).pow(0.5)
    window_size = 5
    df['acc_magnitude_mean'] = df['acc_magnitude'].rolling(window=window_size).mean()
    df['gyro_magnitude_mean'] = df['gyro_magnitude'].rolling(window=window_size).mean()
    df['speed_variation'] = df['speed'].diff(window_size).abs()

    # Fill missing values after feature engineering
    df.fillna(0, inplace=True)

    return df

# Apply feature engineering to all datasets
training_data = add_enhanced_features(training_data)
controlled_test_data = add_enhanced_features(controlled_test_data)
phones_gyroscope_data = add_enhanced_features(phones_gyroscope_data)
phones_accelerometer_data = add_enhanced_features(phones_accelerometer_data)

# Define features to use for scaling and model training
features = [
    'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz', 'speed',
    'acc_magnitude', 'gyro_magnitude', 'jerk', 'gyro_change',
    'acc_magnitude_mean', 'gyro_magnitude_mean', 'speed_variation'
]

# Scale training data
scaler = StandardScaler()
scaled_training_data = scaler.fit_transform(training_data[features])

# Combine scaled data for training
combined_training_data = np.vstack((scaled_training_data))

# Simulate "epochs" for Isolation Forest training
num_epochs = 50
best_model = None
best_score = float('inf')

for epoch in range(num_epochs):
    # Train Isolation Forest
    isolation_forest = IsolationForest(contamination=0.05, random_state=epoch)
    isolation_forest.fit(combined_training_data)

    # Evaluate the model (example: anomaly score mean)
    scores = isolation_forest.decision_function(combined_training_data)
    mean_score = np.mean(scores)

    print(f"Epoch {epoch + 1}/{num_epochs}: Mean Anomaly Score = {mean_score:.4f}")

    # Save the best model based on mean score (or other criteria)
    if mean_score < best_score:
        best_score = mean_score
        best_model = isolation_forest

# Save the best model as a pickle file
with open('../Detection_model_mobile/Trained model/isolation_forest_model.pkl', 'wb') as file:
    pickle.dump(best_model, file)
print("Best Isolation Forest model saved as 'isolation_forest_model.pkl'")
