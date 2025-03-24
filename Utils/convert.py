import pickle
from tensorflow import keras

# Load the .keras model
model1 = keras.models.load_model('C:/Users/anand/Downloads/Projects/Crash Detection System/Trained model/lstm_autoencoder_model.keras')

# Save the model as a pickle file
with open('../Detection_model_mobile/Trained model/lstm_autoencoder_model.pkl', 'wb') as file:
    pickle.dump(model1, file)

import joblib
import pickle

# Load the .joblib model
model2 = joblib.load('/Detection_model_mobile/Trained model/isolation_forest_model.joblib')

# Save the model as a pickle file
with open('../Detection_model_mobile/Trained model/isolation_forest_model.pkl', 'wb') as file:
    pickle.dump(model2, file)
