import time
import os
import joblib
import pandas as pd
from Utils.plot_isolation_forest import *
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from tensorflow.keras.utils import plot_model

start_time = time.time()
# Define data directory
DATA_DIR = "C:/Users/anand/Downloads/Projects/Crash Detection System/Detection_model_mobile"

# Function to load dataset
def load_csv(relative_path):
    return pd.read_csv(os.path.join(DATA_DIR, relative_path))

# Load datasets
datasets = {
    "controlled_test": load_csv("gps_dataset/dataset_controlled_test/data_set_controlled_test.csv"),
    "training": load_csv("gps_dataset/dataset_training/data_set_training.csv"),
    "uncontrolled_test": load_csv("gps_dataset/dataset_uncontrolled_test/data_set_uncontrolled_test.csv"),
    "phones_gyroscope": load_csv("Phones_gyroscope_reduced/Phones_gyroscope1.csv"),
    "phones_accelerometer": load_csv("Phones_accelerometer_reduced/Phones_accelerometer1.csv"),
    "general_table_controlled_test": load_csv("gps_dataset/dataset_controlled_test/General_table_controlled_test.csv"),
    "general_table_training": load_csv("gps_dataset/dataset_training/general_table_training.csv"),
    "general_table_uncontrolled_test": load_csv("gps_dataset/dataset_uncontrolled_test/general_table_uncontrolled_test.csv"),
}

# Rename sensor columns
datasets["phones_gyroscope"].rename(columns={'x': 'gyrox', 'y': 'gyroy', 'z': 'gyroz'}, inplace=True)
datasets["phones_accelerometer"].rename(columns={'x': 'accx', 'y': 'accy', 'z': 'accz'}, inplace=True)

# Add missing columns
for key, df in datasets.items():
    for col in ['speed', 'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz']:
        if col not in df:
            df[col] = np.nan

# Feature Engineering Function
def add_enhanced_features(df):
    df['acc_magnitude'] = np.sqrt(df['accx'] ** 2 + df['accy'] ** 2 + df['accz'] ** 2)
    df['gyro_magnitude'] = np.sqrt(df['gyrox'] ** 2 + df['gyroy'] ** 2 + df['gyroz'] ** 2)
    df['jerk'] = df[['accx', 'accy', 'accz']].diff().pow(2).sum(axis=1).pow(0.5)
    df['gyro_change'] = df[['gyrox', 'gyroy', 'gyroz']].diff().pow(2).sum(axis=1).pow(0.5)
    df['acc_magnitude_mean'] = df['acc_magnitude'].rolling(window=5).mean()
    df['gyro_magnitude_mean'] = df['gyro_magnitude'].rolling(window=5).mean()
    df['speed_variation'] = df['speed'].rolling(5).std()  # Using std instead of diff(window_size)

    df.fillna(0, inplace=True)
    return df

# Apply feature engineering to all datasets
for key in datasets:
    datasets[key] = add_enhanced_features(datasets[key])

# Define features
features = [
    'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz', 'speed',
    'acc_magnitude', 'gyro_magnitude', 'jerk', 'gyro_change',
    'acc_magnitude_mean', 'gyro_magnitude_mean', 'speed_variation'
]

# Scale datasets
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(datasets["training"][features])
scaled_data = {key: scaler.transform(datasets[key][features]) for key in datasets}
# scaled_data = {key: scaler.fit_transform(datasets[key][features]) if "training" in key else scaler.transform(datasets[key][features]) for key in datasets}

# Train Isolation Forest
combined_training_data = np.vstack([
    scaled_data["training"],
    scaled_data["general_table_training"],
    scaled_data["phones_gyroscope"],
    scaled_data["phones_accelerometer"]
])

isolation_forest = IsolationForest(contamination=0.05, random_state=42)
isolation_forest.fit(combined_training_data)

# Save isolation forest visualizations
# visualize_isolation_tree(isolation_forest, features)
# plot_isolation_feature_importance(isolation_forest, features)

# Apply Isolation Forest
for key in ["controlled_test", "uncontrolled_test", "general_table_controlled_test", "general_table_uncontrolled_test"]:
    datasets[key]['IF_anomaly'] = isolation_forest.predict(scaled_data[key])

# Prepare LSTM Data
sequence_length = 10
X_train = np.array([combined_training_data[i:i + sequence_length] for i in range(len(combined_training_data) - sequence_length)])

# Build LSTM Autoencoder
model = Sequential([
    LSTM(32, activation="relu", input_shape=(sequence_length, X_train.shape[2]), return_sequences=True,
         kernel_regularizer=l2(0.005)),
    Dropout(0.3),
    LSTM(16, activation="relu", return_sequences=False, kernel_regularizer=l2(0.01)),  # Increased L2
    RepeatVector(sequence_length),
    LSTM(16, activation="relu", return_sequences=True, kernel_regularizer=l2(0.01)),
    Dropout(0.3),
    LSTM(32, activation="relu", return_sequences=True, kernel_regularizer=l2(0.01)),
    TimeDistributed(Dense(X_train.shape[2]))
])

# Save LSTM autoencoder Layer Structure
# plot_model(model, to_file='lstm_autoencoder_model_structure.png', show_shapes=True, show_layer_names=True)

# Compile and Train LSTM Model
model.compile(optimizer=Adam(learning_rate=0.0005, clipnorm=1.0), loss="mse")
early_stopping = EarlyStopping(monitor="loss", patience=5, restore_best_weights=True)
history = model.fit(X_train, X_train, epochs=50, batch_size=32, validation_split=0.1, callbacks=[early_stopping])

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.show()

# Compute LSTM reconstruction error
def reshape_data(df):
    data = scaler.transform(df[features])
    return np.array([data[i:i + sequence_length] for i in range(len(data) - sequence_length)])

test_errors = {key: np.mean(np.square(model.predict(reshape_data(datasets[key])) - reshape_data(datasets[key])), axis=(1, 2)) for key in ["controlled_test", "general_table_controlled_test"]}

# Hybrid Anomaly Detection
alpha, beta = 0.6, 0.4
max_error = max(test_errors["controlled_test"].max(), test_errors["general_table_controlled_test"].max())

threshold_controlled = np.percentile(test_errors["controlled_test"], 95)  # Top 5% most anomalous points
threshold_general = np.percentile(test_errors["general_table_controlled_test"], 95)

for key in ["controlled_test", "general_table_controlled_test"]:
    df = datasets[key].iloc[sequence_length:].copy()
    df['IF_score'] = (df['IF_anomaly'] == -1).astype(int)
    df['LSTM_score'] = test_errors[key] / max_error
    df['hybrid_score'] = alpha * df['IF_score'] + beta * df['LSTM_score']
    df['hybrid_anomaly'] = (df['hybrid_score'] > (threshold_controlled if key == "controlled_test" else threshold_general)).astype(int)

    print(f"Hybrid Anomalies in {key}:")
    print(df[df['hybrid_anomaly'] == 1])

# Save models
joblib.dump(isolation_forest, 'Trained model/isolation_forest_model_xs.joblib')
model.save('Trained model/lstm_autoencoder_model_xs.keras')
end_time = time.time()
total_time = end_time - start_time

if total_time >= 3600:  # More than an hour
    print(f"Total Execution Time: {total_time / 3600:.2f} hours")
elif total_time >= 60:  # More than a minute
    print(f"Total Execution Time: {total_time / 60:.2f} minutes")
else:
    print(f"Total Execution Time: {total_time:.2f} seconds")
