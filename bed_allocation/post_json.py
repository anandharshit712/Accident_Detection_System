import json
from pymongo import MongoClient

# MongoDB Atlas Connection
client = MongoClient("mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb")  # Replace <connection_string> with your Atlas URI
db = client["test"]  # Replace with your database name
collection = db["accidents"]  # Replace with your collection name

# Load the JSON file
# def load_json_file(file_path):
#     try:
#         with open(file_path, 'r') as file:
#             data = json.load(file)
#         print(f"Loaded {len(data)} records from {file_path}")
#         return data
#     except Exception as e:
#         print(f"Error loading JSON file: {e}")
#         return None

# Post JSON data to MongoDB Atlas
def post_to_mongodb(json_data):
    if not json_data:
        print("No data to post to MongoDB.")
        return
    try:
        result = collection.insert_many(json_data)
        print(f"Successfully inserted {len(result.inserted_ids)} records into MongoDB Atlas.")
    except Exception as e:
        print(f"Error posting data to MongoDB: {e}")

# Main execution
# if __name__ == "__main__":
#     # Path to the JSON file generated by the anomaly detection script
#     json_file_path = "accident_status.json"
#
#     # Load JSON data
#     data = load_json_file(json_file_path)
#
#     # Post data to MongoDB
#     post_to_mongodb(data)
