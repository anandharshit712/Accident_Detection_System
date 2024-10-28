import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load the dataset (already loaded in 'training_data')

# Function to calculate magnitude from x, y, z components
def calculate_magnitude(x, y, z):
    return np.sqrt(x**2 + y**2 + z**2)

# Adding acceleration magnitude and gyroscope magnitude
training_data['accel_magnitude'] = calculate_magnitude(
    training_data['accx'], training_data['accy'], training_data['accz']
)

training_data['gyro_magnitude'] = calculate_magnitude(
    training_data['gyrox'], training_data['gyroy'], training_data['gyroz']
)

# Calculating speed change (difference between consecutive speed values)
training_data['speed_change'] = training_data['speed'].diff().fillna(0)

# Selecting only the relevant features for the model
features = ['accel_magnitude', 'gyro_magnitude', 'speed_change']

# Step 2: Normalizing the data (scaling)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(training_data[features])

# Create a DataFrame with scaled features
scaled_features_df = pd.DataFrame(X_scaled, columns=features)
