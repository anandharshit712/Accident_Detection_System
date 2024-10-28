import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.ensemble import IsolationForest

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

# Define sequence length for LSTM
sequence_length = 10  # Define the length of each sequence
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

# Reshape test data for anomaly detection
def reshape_data_for_lstm(df, features, sequence_length):
    data = scaler.transform(df[features])
    sequences = []
    for i in range(len(data) - sequence_length):
        sequences.append(data[i:i + sequence_length])
    return np.array(sequences)

X_controlled_test = reshape_data_for_lstm(controlled_test_data, features, sequence_length)
X_uncontrolled_test = reshape_data_for_lstm(uncontrolled_test_data, features, sequence_length)

# Predict and calculate reconstruction error for test data
def calculate_reconstruction_error(model, data):
    predictions = model.predict(data)
    reconstruction_errors = np.mean(np.square(predictions - data), axis=(1, 2))
    return reconstruction_errors

controlled_test_errors = calculate_reconstruction_error(model, X_controlled_test)
uncontrolled_test_errors = calculate_reconstruction_error(model, X_uncontrolled_test)

# Set anomaly threshold based on training data reconstruction error
threshold = np.percentile(calculate_reconstruction_error(model, X_train), 95)

# Create a DataFrame to store sequence-based anomaly results for controlled and uncontrolled test sets
controlled_test_sequences = controlled_test_data.iloc[sequence_length:].copy()
uncontrolled_test_sequences = uncontrolled_test_data.iloc[sequence_length:].copy()

# Detect anomalies based on threshold
controlled_test_sequences['anomaly'] = [1 if error > threshold else 0 for error in controlled_test_errors]
uncontrolled_test_sequences['anomaly'] = [1 if error > threshold else 0 for error in uncontrolled_test_errors]

# Display anomalies
print("Controlled Test Anomalies:")
print(controlled_test_sequences[controlled_test_sequences['anomaly'] == 1].head())

print("\nUncontrolled Test Anomalies:")
print(uncontrolled_test_sequences[uncontrolled_test_sequences['anomaly'] == 1].head())
