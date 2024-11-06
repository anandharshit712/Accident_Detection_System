import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Load data
controlled_test_data = pd.read_csv("gps_dataset/dataset_controlled_test/data_set_controlled_test.csv")
training_data = pd.read_csv("gps_dataset/dataset_training/data_set_training.csv")
uncontrolled_test_data = pd.read_csv("gps_dataset/dataset_uncontrolled_test/data_set_uncontrolled_test.csv")

# Feature Engineering
def add_enhanced_features(df):
    df['acc_magnitude'] = np.sqrt(df['accx']**2 + df['accy']**2 + df['accz']**2)
    df['gyro_magnitude'] = np.sqrt(df['gyrox']**2 + df['gyroy']**2 + df['gyroz']**2)
    df['jerk'] = df[['accx', 'accy', 'accz']].diff().pow(2).sum(axis=1).pow(0.5)
    df['gyro_change'] = df[['gyrox', 'gyroy', 'gyroz']].diff().pow(2).sum(axis=1).pow(0.5)
    window_size = 5
    df['acc_magnitude_mean'] = df['acc_magnitude'].rolling(window=window_size).mean()
    df['gyro_magnitude_mean'] = df['gyro_magnitude'].rolling(window=window_size).mean()
    df['speed_variation'] = df['speed'].diff(window_size).abs()
    return df

# Apply feature engineering to datasets
training_data = add_enhanced_features(training_data).dropna()
controlled_test_data = add_enhanced_features(controlled_test_data).dropna()
uncontrolled_test_data = add_enhanced_features(uncontrolled_test_data).dropna()

# Select features for anomaly detection
features = [
    'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz', 'speed',
    'acc_magnitude', 'gyro_magnitude', 'jerk', 'gyro_change',
    'acc_magnitude_mean', 'gyro_magnitude_mean', 'speed_variation'
]
scaler = StandardScaler()
scaled_training_data = scaler.fit_transform(training_data[features])

# Isolation Forest for Static Anomaly Detection
isolation_forest = IsolationForest(contamination=0.05, random_state=42)
isolation_forest.fit(scaled_training_data)

# Apply Isolation Forest to detect anomalies in test sets
controlled_test_scaled = scaler.transform(controlled_test_data[features])
uncontrolled_test_scaled = scaler.transform(uncontrolled_test_data[features])

controlled_test_data['IF_anomaly'] = isolation_forest.predict(controlled_test_scaled)
uncontrolled_test_data['IF_anomaly'] = isolation_forest.predict(uncontrolled_test_scaled)

# Define sequence length for LSTM
sequence_length = 10
X_train = []
for i in range(len(scaled_training_data) - sequence_length):
    X_train.append(scaled_training_data[i:i + sequence_length])

X_train = np.array(X_train)

# LSTM Autoencoder Model
model = Sequential([
    LSTM(64, activation="relu", input_shape=(sequence_length, X_train.shape[2]), return_sequences=True),
    LSTM(32, activation="relu", return_sequences=False),
    RepeatVector(sequence_length),
    LSTM(32, activation="relu", return_sequences=True),
    LSTM(64, activation="relu", return_sequences=True),
    TimeDistributed(Dense(X_train.shape[2]))
])

model.compile(optimizer=Adam(learning_rate=0.001), loss="mse")

# Training the model with early stopping
early_stopping = EarlyStopping(monitor="loss", patience=5, restore_best_weights=True)
history = model.fit(X_train, X_train, epochs=50, batch_size=32, validation_split=0.1, callbacks=[early_stopping])

# Reshape test data for anomaly detection with LSTM
def reshape_data_for_lstm(df, features, sequence_length):
    data = scaler.transform(df[features])
    sequences = []
    for i in range(len(data) - sequence_length):
        sequences.append(data[i:i + sequence_length])
    return np.array(sequences)

X_controlled_test = reshape_data_for_lstm(controlled_test_data, features, sequence_length)
X_uncontrolled_test = reshape_data_for_lstm(uncontrolled_test_data, features, sequence_length)

# Calculate reconstruction error for LSTM
def calculate_reconstruction_error(model, data):
    predictions = model.predict(data)
    reconstruction_errors = np.mean(np.square(predictions - data), axis=(1, 2))
    return reconstruction_errors

controlled_test_errors = calculate_reconstruction_error(model, X_controlled_test)
uncontrolled_test_errors = calculate_reconstruction_error(model, X_uncontrolled_test)

# Set weights for weighted scoring approach
alpha, beta = 0.6, 0.4  # Adjust weights based on importance or reliability of each model

# Normalize Isolation Forest anomaly to 0 and 1
controlled_test_sequences = controlled_test_data.iloc[sequence_length:].copy()
controlled_test_sequences['IF_score'] = (controlled_test_sequences['IF_anomaly'] == -1).astype(int)

# Normalize LSTM reconstruction error and scale between 0 and 1
max_error = controlled_test_errors.max()
controlled_test_sequences['LSTM_score'] = controlled_test_errors / max_error

# Calculate hybrid score as a weighted sum of IF_score and LSTM_score
controlled_test_sequences['hybrid_score'] = (
    alpha * controlled_test_sequences['IF_score'] +
    beta * controlled_test_sequences['LSTM_score']
)

# Set a threshold on the hybrid score to classify as an anomaly
threshold = 0.5  # Adjust based on desired sensitivity
controlled_test_sequences['hybrid_anomaly'] = (controlled_test_sequences['hybrid_score'] > threshold).astype(int)

# Display anomalies based on weighted scoring
print("Controlled Test Anomalies (Weighted Hybrid):")
print(controlled_test_sequences[controlled_test_sequences['hybrid_anomaly'] == 1])

# Assuming `isolation_forest` is trained as shown in the previous code
# Save the Isolation Forest model
joblib.dump(isolation_forest, 'isolation_forest_model.joblib')
print("Isolation Forest model saved as isolation_forest_model.joblib")

# Save the LSTM Autoencoder model
model.save('lstm_autoencoder_model.keras')
print("LSTM Autoencoder model saved as lstm_autoencoder_model.h5")
