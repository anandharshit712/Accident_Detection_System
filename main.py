import time
import subprocess
import pymongo
from datetime import datetime

# MongoDB client setup
client = pymongo.MongoClient("mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb")
db = client["test"]
beds_collection = db["beds"]
accident_collection = db["accident"]

def run_sensor_model():
    print(f"[{datetime.now()}] Running sensor-based accident detection...")
    result = subprocess.run(["python", "Detection_model_mobile/model_backend.py"])
    return result.returncode == 1  # Assume 1 = accident detected

def run_video_model():
    print(f"[{datetime.now()}] Running video-based accident detection...")
    result = subprocess.run(["python", "Detection_model_mobile/FINAL_PREDICTION.py"])
    return result.returncode == 1  # Assume 1 = accident detected

def record_accident():
    accident_data = {
        "timestamp": datetime.now(),
        "source": "sensor+video",
        "status": "detected"
    }
    accident_collection.insert_one(accident_data)
    print(f"[{datetime.now()}] 🚨 Accident detected and recorded!")

def run_bed_allocation():
    print(f"[{datetime.now()}] Running bed allocation algorithm...")
    subprocess.run(["python", "bed_allocation/single_file_integration.py"])

def check_new_beds_data():
    latest_entry = beds_collection.find_one({"status": True}, sort=[("timestamp", pymongo.DESCENDING)])
    if latest_entry:
        beds_collection.update_one({"_id": latest_entry["_id"]}, {"$set": {"status": False}})
        return True
    return False

if __name__ == "__main__":
    print("[STARTED] Automation controller running...")
    while True:
        start_time = time.time()

        # Step 1: Accident Detection (sensor + video)
        sensor_result = run_sensor_model()
        video_result = run_video_model()

        if sensor_result or video_result:
            record_accident()

        # Step 2: Check Beds DB for new survey data to run bed allocation
        if check_new_beds_data():
            run_bed_allocation()

        # Sleep to maintain 5-second interval
        elapsed = time.time() - start_time
        time.sleep(max(0, 5 - elapsed))
