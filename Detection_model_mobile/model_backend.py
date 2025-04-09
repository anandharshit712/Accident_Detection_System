import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import pickle
import json
from multiprocessing import Process, JoinableQueue, Manager
from database_connection import fetch_documents_from_mongodb
from bed_allocation.post_json import post_to_mongodb
from datetime import datetime
import time

# Load model once per process (not globally shared)
isolation_forest_model = None
lstm_model = None

# Loading models from pkl file
def load_models():
    with open('C:/Users/anand/Downloads/Projects/Crash Detection System/Detection_model_mobile/Trained model/isolation_forest_model_xs.pkl', 'rb') as file:
        isolation_forest_model = pickle.load(file)
    with open('C:/Users/anand/Downloads/Projects/Crash Detection System/Detection_model_mobile/Trained model/lstm_autoencoder_model_xs.pkl', 'rb') as file:
        lstm_model = pickle.load(file)
    return isolation_forest_model, lstm_mode

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def save_accident_to_json(data):
    if not data or not isinstance(data, list):
        print("Warning: Tried to save empty or invalid accident data.")
        return
    filename = f'../accident_status_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.json'
    with open(filename, 'w') as j:
        json.dump(data, j, indent=4, cls=DateTimeEncoder)

def calculate_additional_features(data_entry, batch_speeds):
    accelX, accelY, accelZ = data_entry['accelX'], data_entry['accelY'], data_entry['accelZ']
    acc_magnitude = np.sqrt(accelX**2 + accelY**2 + accelZ**2)
    gyroX, gyroY, gyroZ = data_entry['gyroX'], data_entry['gyroY'], data_entry['gyroZ']
    gyro_magnitude = np.sqrt(gyroX**2 + gyroY**2 + gyroZ**2)
    jerk = np.abs(accelX - accelY)
    gyro_change = np.abs(gyroX - gyroY)
    acc_magnitude_mean = acc_magnitude
    gyro_magnitude_mean = gyro_magnitude
    speed_variation = np.std(batch_speeds) if len(batch_speeds) > 1 else 0
    return [
        accelX, accelY, accelZ, gyroX, gyroY, gyroZ, data_entry['speed'],
        acc_magnitude, gyro_magnitude, jerk, gyro_change,
        acc_magnitude_mean, gyro_magnitude_mean, speed_variation
    ]

def calculate_weights(if_scores, lstm_scores):
    if_variance = np.var(if_scores)
    lstm_variance = np.var(lstm_scores)
    total_variance = if_variance + lstm_variance
    if total_variance == 0:
        return 0.5, 0.5
    return if_variance / total_variance, lstm_variance / total_variance

def worker(queue, results):
    global isolation_forest_model, lstm_model
    if isolation_forest_model is None or lstm_model is None:
        isolation_forest_model, lstm_model = load_models()
    while True:
        task = queue.get()
        if task is None:
            break
        user, data_entries = task
        if len(data_entries) < 5:
            queue.task_done()
            continue

        batch_speeds = [entry['speed'] for entry in data_entries]
        batch_features = [calculate_additional_features(entry, batch_speeds) for entry in data_entries]
        batch_array = np.array(batch_features)

        if_scores = isolation_forest_model.decision_function(batch_array)
        if_scores = (if_scores - np.min(if_scores)) / (np.max(if_scores) - np.min(if_scores) + 1e-8)

        sequence_length = 10
        if batch_array.shape[0] < sequence_length:
            pad_length = sequence_length - batch_array.shape[0]
            pad_array = np.zeros((pad_length, batch_array.shape[1]))
            batch_array_padded = np.vstack([pad_array, batch_array])
        else:
            batch_array_padded = batch_array[-sequence_length:]

        lstm_input = batch_array_padded.reshape((1, sequence_length, batch_array.shape[1]))
        lstm_reconstruction = lstm_model.predict(lstm_input)[0]
        lstm_error = np.mean(np.square(lstm_reconstruction - batch_array_padded), axis=1)
        lstm_scores = (lstm_error - np.min(lstm_error)) / (np.max(lstm_error) - np.min(lstm_error) + 1e-8)
        lstm_scores = lstm_scores[-len(if_scores):]  # Align with if_scores

        if_weight, lstm_weight = calculate_weights(if_scores, lstm_scores)
        hybrid_scores = if_weight * if_scores + lstm_weight * lstm_scores
        dynamic_threshold = np.percentile(hybrid_scores, 95)
        is_accident = np.count_nonzero(hybrid_scores > dynamic_threshold) >= 3

        accident_data = {
            "mobile_number": user,
            "lat": data_entries[0].get('lat') or data_entries[0].get('latitude'),
            "long": data_entries[0].get('long') or data_entries[0].get('longitude'),
            "status": is_accident,
            "timestamp": datetime.now()
        }
        print(f"[{user}] IF scores: {if_scores}")
        print(f"[{user}] LSTM scores: {lstm_scores}")
        print(f"[{user}] Hybrid scores: {hybrid_scores}")

        if is_accident:
            save_accident_to_json([accident_data])
            post_to_mongodb([accident_data])

        results.append(accident_data)
        queue.task_done()

def process_all_users_dynamic():
    user_data = fetch_documents_from_mongodb()
    task_queue = JoinableQueue(maxsize=10)
    manager = Manager()
    results = manager.list()

    processes = []
    initial_workers = 4

    for _ in range(initial_workers):
        p = Process(target=worker, args=(task_queue, results))
        p.start()
        processes.append(p)

    for user, data in user_data.items():
        if task_queue.full():
            p = Process(target=worker, args=(task_queue, results))
            p.start()
            processes.append(p)
        task_queue.put((user, data))

    task_queue.join()

    for _ in processes:
        task_queue.put(None)
    for p in processes:
        p.join()

    return list(results)

if __name__ == '__main__':
    start = time.time()
    final_results = process_all_users_dynamic()
    end = time.time()

    for result in final_results:
        print(f"User: {result['mobile_number']} - Accident Detected: {result['status']}")

    duration = end - start
    if duration >= 3600:
        print(f"Total Time: {duration / 3600:.2f} hours")
    elif duration >= 60:
        print(f"Total Time: {duration / 60:.2f} minutes")
    else:
        print(f"Total Time: {duration:.2f} seconds")
