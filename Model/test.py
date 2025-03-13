import pandas as pd

# Load the CSV file
file_path = 'Phones_accelerometer_reduced/Phones_accelerometer1.csv'
df = pd.read_csv(file_path)

# Remove rows with null values
df = df.dropna()

# Save the cleaned data back to the same file
df.to_csv(file_path, index=False)

print("Null values removed and file saved.")


model = Sequential([
    LSTM(32, activation="relu", input_shape=(sequence_length, X_train.shape[2]), return_sequences=True, kernel_regularizer=l2(0.001)),
    Dropout(0.4),  # Increase dropout rate
    LSTM(16, activation="relu", return_sequences=False, kernel_regularizer=l2(0.001)),
    RepeatVector(sequence_length),
    LSTM(16, activation="relu", return_sequences=True, kernel_regularizer=l2(0.001)),
    Dropout(0.4),
    LSTM(32, activation="relu", return_sequences=True, kernel_regularizer=l2(0.001)),
    Dropout(0.4),
    TimeDistributed(Dense(X_train.shape[2]))
])
