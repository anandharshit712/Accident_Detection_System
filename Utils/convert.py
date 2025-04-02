import pickle
from tensorflow import keras

# Load the .keras model
model1 = keras.models.load_model('C:/Users/anand/Downloads/Projects/Crash Detection System/Detection_model_mobile/Trained model/lstm_autoencoder_model_xs.keras')

# Save the model as a pickle file
with open('../Detection_model_mobile/Trained model/lstm_autoencoder_model_xs.pkl', 'wb') as file:
    pickle.dump(model1, file)

import joblib
import pickle

# Load the .joblib model
model2 = joblib.load('C:/Users/anand/Downloads/Projects/Crash Detection System/Detection_model_mobile/Trained model/isolation_forest_model_xs.joblib')

# Save the model as a pickle file
with open('../Detection_model_mobile/Trained model/isolation_forest_model_xs.pkl', 'wb') as file:
    pickle.dump(model2, file)
