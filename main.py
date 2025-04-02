import time
import subprocess
import pymongo
from datetime import datetime

# MongoDB client setup
client = pymongo.MongoClient("mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb")  # Replace with your actual URI
db = client["test"]
beds_collection = db["beds"]

# Store last processed timestamp
last_beds_timestamp = None

def run_accident_backend():
    print(f"[{datetime.now()}] Running accident detection backend...")
    subprocess.run(["python", "Detection_model_mobile/model_backend.py"])  # Ensure this script is executable

def run_bed_allocation():
    print(f"[{datetime.now()}] Running bed allocation algorithm...")
    subprocess.run(["python", "bed_allocation/single_file_integration.py"])  # Path to your bed allocation script

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

        # Step 1: Accident Detection (runs every 5 seconds)
        run_accident_backend()

        # Step 2: Check Beds DB for new survey data to run bed allocation
        if check_new_beds_data():
            run_bed_allocation()

        # Sleep for remaining time in 5-second interval
        elapsed = time.time() - start_time
        sleep_time = max(0, 5 - elapsed)
        time.sleep(sleep_time)
