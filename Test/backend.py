import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Load all datasets, including the new Phones Gyroscope and Accelerometer datasets
controlled_test_data = pd.read_csv("gps_dataset/dataset_controlled_test/data_set_controlled_test.csv")
training_data = pd.read_csv("gps_dataset/dataset_training/data_set_training.csv")
uncontrolled_test_data = pd.read_csv("gps_dataset/dataset_uncontrolled_test/data_set_uncontrolled_test.csv")
phones_gyroscope_data = pd.read_csv("Phones_gyroscope/Phones_gyroscope.csv")
phones_accelerometer_data = pd.read_csv("Phones_accelerometer/Phones_accelerometer.csv")

# Rename columns in the new datasets to match expected feature names
phones_gyroscope_data = phones_gyroscope_data.rename(columns={'x': 'gyrox', 'y': 'gyroy', 'z': 'gyroz'})
phones_accelerometer_data = phones_accelerometer_data.rename(columns={'x': 'accx', 'y': 'accy', 'z': 'accz'})

# Add dummy columns for missing fields (assuming `speed` is missing)
for col in ['speed', 'accx', 'accy', 'accz']:
    if col not in phones_gyroscope_data:
        phones_gyroscope_data[col] = np.nan

for col in ['speed', 'gyrox', 'gyroy', 'gyroz']:
    if col not in phones_accelerometer_data:
        phones_accelerometer_data[col] = np.nan


# Feature Engineering function
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
uncontrolled_test_data = add_enhanced_features(uncontrolled_test_data)
phones_gyroscope_data = add_enhanced_features(phones_gyroscope_data)
phones_accelerometer_data = add_enhanced_features(phones_accelerometer_data)

# Define features to use for scaling and model training
features = [
    'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz', 'speed',
    'acc_magnitude', 'gyro_magnitude', 'jerk', 'gyro_change',
    'acc_magnitude_mean', 'gyro_magnitude_mean', 'speed_variation'
]

# Scale training data and the new datasets
scaler = StandardScaler()
scaled_training_data = scaler.fit_transform(training_data[features])

if not phones_gyroscope_data[features].empty:
    scaled_phones_gyroscope_data = scaler.transform(phones_gyroscope_data[features])
else:
    print("The phones_gyroscope_data is empty after preprocessing.")
    scaled_phones_gyroscope_data = np.empty((0, len(features)))  # or handle appropriately

if not phones_accelerometer_data[features].empty:
    scaled_phones_accelerometer_data = scaler.transform(phones_accelerometer_data[features])
else:
    print("The phones_accelerometer_data is empty after preprocessing.")
    scaled_phones_accelerometer_data = np.empty((0, len(features)))  # or handle appropriately

# Combine scaled data for Isolation Forest training
combined_training_data = np.vstack(
    (scaled_training_data, scaled_phones_gyroscope_data, scaled_phones_accelerometer_data))

# Train Isolation Forest model
isolation_forest = IsolationForest(contamination=0.05, random_state=42)
isolation_forest.fit(combined_training_data)

# Apply Isolation Forest to detect anomalies in test data
controlled_test_scaled = scaler.transform(controlled_test_data[features])
uncontrolled_test_scaled = scaler.transform(uncontrolled_test_data[features])

controlled_test_data['IF_anomaly'] = isolation_forest.predict(controlled_test_scaled)
uncontrolled_test_data['IF_anomaly'] = isolation_forest.predict(uncontrolled_test_scaled)

# Define sequence length for LSTM model
sequence_length = 10
X_train = [combined_training_data[i:i + sequence_length] for i in range(len(combined_training_data) - sequence_length)]
X_train = np.array(X_train)

# Build LSTM Autoencoder model
model = Sequential([
    LSTM(64, activation="relu", input_shape=(sequence_length, X_train.shape[2]), return_sequences=True),
    LSTM(32, activation="relu", return_sequences=False),
    RepeatVector(sequence_length),
    LSTM(32, activation="relu", return_sequences=True),
    LSTM(64, activation="relu", return_sequences=True),
    TimeDistributed(Dense(X_train.shape[2]))
])

model.compile(optimizer=Adam(learning_rate=0.001), loss="mse")

# Train the model with early stopping
early_stopping = EarlyStopping(monitor="loss", patience=5, restore_best_weights=True)
history = model.fit(X_train, X_train, epochs=50, batch_size=32, validation_split=0.1, callbacks=[early_stopping])


# Reshape test data for LSTM
def reshape_data_for_lstm(df, features, sequence_length):
    data = scaler.transform(df[features])
    sequences = [data[i:i + sequence_length] for i in range(len(data) - sequence_length)]
    return np.array(sequences)


# Apply LSTM anomaly detection on test data
X_controlled_test = reshape_data_for_lstm(controlled_test_data, features, sequence_length)
X_uncontrolled_test = reshape_data_for_lstm(uncontrolled_test_data, features, sequence_length)


# Calculate reconstruction error
def calculate_reconstruction_error(model, data):
    predictions = model.predict(data)
    reconstruction_errors = np.mean(np.square(predictions - data), axis=(1, 2))
    return reconstruction_errors


controlled_test_errors = calculate_reconstruction_error(model, X_controlled_test)
uncontrolled_test_errors = calculate_reconstruction_error(model, X_uncontrolled_test)

# Weighted scoring with Isolation Forest and LSTM
alpha, beta = 0.6, 0.4
max_error = controlled_test_errors.max()
controlled_test_sequences = controlled_test_data.iloc[sequence_length:].copy()
controlled_test_sequences['IF_score'] = (controlled_test_sequences['IF_anomaly'] == -1).astype(int)
controlled_test_sequences['LSTM_score'] = controlled_test_errors / max_error
controlled_test_sequences['hybrid_score'] = (
        alpha * controlled_test_sequences['IF_score'] +
        beta * controlled_test_sequences['LSTM_score']
)

threshold = 0.5
controlled_test_sequences['hybrid_anomaly'] = (controlled_test_sequences['hybrid_score'] > threshold).astype(int)

# Display anomalies
print("Controlled Test Anomalies (Weighted Hybrid):")
print(controlled_test_sequences[controlled_test_sequences['hybrid_anomaly'] == 1])

# Save the models
joblib.dump(isolation_forest, 'isolation_forest_model.joblib')
model.save('lstm_autoencoder_model.keras')