import pymongo

def fetch_documents_from_mongodb():
    # MongoDB Atlas connection string
    CONNECTION_STRING = "mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb"

    # Establish a connection to MongoDB
    client = pymongo.MongoClient(CONNECTION_STRING)

    # database access
    database = client["test"]

    # collection
    collection = database["sensordatas"]
    # collection = database["accidents"]

    # Fetch data from the collection
    user_ids = collection.distinct("ID")

    # Loop through each phone number and get their latest 5-second batch
    all_user_data = {}

    for user_id in user_ids:
        query = {"ID": user_id}
        latest_data = list(collection.find(query).sort("timestamp", pymongo.DESCENDING).limit(5))
        all_user_data[user_id] = latest_data

    return all_user_data


# Example usage
docs = fetch_documents_from_mongodb()
for user_id, data in docs.items():
    print(f"User {user_id}:\nData: \n{data}")
