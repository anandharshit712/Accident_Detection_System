import pickle
from tensorflow import keras

# Load the .keras model
model1 = keras.models.load_model('dense_autoencoder_model_Dense_NN.keras')

# Save the model as a pickle file
with open('dense_autoencoder_model_Dense_NN.pkl', 'wb') as file:
    pickle.dump(model1, file)

import joblib
import pickle

# Load the .joblib model
model2 = joblib.load('isolation_forest_model_Dense_NN.joblib')

# Save the model as a pickle file
with open('isolation_forest_model_Dense_NN.pkl', 'wb') as file:
    pickle.dump(model2, file)
