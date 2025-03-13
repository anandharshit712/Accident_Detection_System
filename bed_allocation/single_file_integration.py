from pymongo import MongoClient
import numpy as np
from queue import PriorityQueue
import math


def post_to_mongodb(json_data,collection):
    if not json_data:
        print("No data to post to MongoDB.")
        return
    try:
        result = collection.insert_many(json_data)
        print(f"Successfully inserted {len(result.inserted_ids)} records into MongoDB Atlas.")
    except Exception as e:
        print(f"Error posting data to MongoDB: {e}")


def fetch_beds_data():
    max_documents_per_user = 5
    connection_string = "mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb"
    database_name = "test"
    collection_name = "beds"
    """
    Fetch a specified number of documents per user (grouped by 'mobileNumber') from a MongoDB collection.

    Parameters:
    - connection_string (str): The MongoDB Atlas connection string.
    - database_name (str): Name of the database to connect to.
    - collection_name (str): Name of the collection to query.
    - max_documents_per_user (int): Maximum number of documents to fetch per user. Default is 5.

    Returns:
    - dict: A dictionary where keys are 'mobileNumber' values and values are lists of documents.
    """
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]
        # Aggregation pipeline
        pipeline = [
            {"$sort": {"_id": 1}},  # Sort documents by '_id' or any other field for consistent ordering
            {"$group": {
                "_id": "$mobileNumber",  # Group by 'mobileNumber'
                "documents": {"$push": "$$ROOT"}  # Collect all documents for each user
            }},
            {"$project": {
                "mobileNumber": "$_id",  # Rename '_id' to 'mobileNumber'
                "documents": {"$slice": ["$documents", max_documents_per_user]}  # Limit to max_documents_per_user
            }}
        ]
        # Execute the aggregation pipeline
        result = collection.aggregate(pipeline)
        # Store the fetched data into a dictionary
        user_data_dict = {
            user_data.get('mobileNumber'): user_data['documents']
            for user_data in result
        }

        return user_data_dict, collection
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def fetch_no_of_beds(user_data,collection):
    no_of_beds_list,lat,long,mob = [],[],[],[]
    for mobile_number, documents in user_data.items():
        for doc in documents:
            no_of_beds_list.append(doc['no_of_beds'])
            lat.append(doc['lat'])
            long.append(doc['long'])
            mob.append(doc['mobile_number'])
            update_status_to_false(collection)
    return no_of_beds_list,lat,long,mob


def update_status_to_false(collection):
    try: # Update the 'status' field to False for all documents
        update_result = collection.update_many({}, {"$set": {"status": False}}) # Print the number of documents updated
        print(f"Matched {update_result.matched_count} documents and updated {update_result.modified_count} documents.")
    except Exception as e:
        print(f"An error occurred: {e}")


def fetch_hospital_data():
    connection_string = "mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb"
    database_name = "test"
    collection_name = "hospitals"  # Replace this with your actual collection name

    try:
        # Connect to MongoDB Atlas
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]

        # Fetch all hospital data
        hospitals = collection.find()

        # Store the fetched data into a dictionary
        hospital_data_dict = {}
        for hospital in hospitals:
            hospital_id = hospital['hospitalID']
            hospital_data_dict[hospital_id] = {
                "latitude": hospital['latitude'],
                "longitude": hospital['longitude'],
                "total_of_available_beds": hospital['total_of_available_beds'],
                "no_of_available_beds": hospital['no_of_available_beds']
            }

        return hospital_data_dict

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def appox(data):
    # Identify outliers using the IQR method
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Remove outliers
    filtered_data = [x for x in data if lower_bound <= x <= upper_bound]

    # Calculate the average
    average = np.mean(filtered_data)
    return round(average)


def return_priority_queue(lat, long, hospital_dict):
    pq = PriorityQueue()

    def euclidean_distance(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

    def find_k_nearest_neighbors(input_coordinate, k=10):
        distances = []
        for hid, details in hospital_dict.items():
            lati = details['latitude']
            longi = details['longitude']
            distance = euclidean_distance(input_coordinate, (lati,longi))
            distances.append((hid, distance))

        distances.sort(key=lambda x: x[1])
        nearest_neighbors = distances[:k]
        return nearest_neighbors

    input_coordinate = (lat, long)
    nearest_hospitals = find_k_nearest_neighbors(input_coordinate)

    for hid, distance in nearest_hospitals:
        pq.put((distance, hid))

    def convert_pq_to_list(pq):
        pq_list = []
        while not pq.empty():
            pq_list.append(pq.get())
        return pq_list

    return convert_pq_to_list(pq)


def acquire_beds(hospital_queue, avg_bed, hospital_dict):
    bed_allocation = {}
    beds_required = avg_bed
    while beds_required > 0 and hospital_queue :
        element = hospital_queue.pop(0)
        distance, h_id = element[0],element[1]

        def get_bed_value_by_id(hospital_id):
            for hid, details in hospital_dict.items():
                if hid == hospital_id:
                    return details['no_of_available_beds']
            return None  # Return None if the Id is not found

        bed_value = get_bed_value_by_id(h_id)
        if bed_value <= beds_required:
            bed_allocation['h_id'] = h_id
            bed_allocation['bed_value'] = beds_required
            beds_required -= bed_value
        else:
            bed_allocation['h_id'] = h_id
            bed_allocation['bed_value'] = beds_required
            beds_required = 0
        print(f"Acquired {bed_allocation['bed_value']} beds from hospital {bed_allocation['h_id']}")
    return bed_allocation


def main_driver():
    # Fetch user data
    user_data, beds_collection = fetch_beds_data()
    print(user_data)
    # Print the fetched data
    print("Fetched Data Dictionary:")
    for mobile_number, documents in user_data.items():
        print("Data:")
        for doc in documents:
            print(doc)

    # Fetch hospital data
    hospital_dict = fetch_hospital_data()
    # Print the fetched data
    print("Fetched Hospital Data Dictionary:")
    for hospital_id, data in hospital_dict.items():
        print(f"Hospital ID: {hospital_id}")
        print("Data:")
        for key, value in data.items():
            print(f"  {key}: {value}")

    Id_map_accident = {}
    no_of_beds, latitudes, longitudes, mob = fetch_no_of_beds(user_data,beds_collection)
    print(f"no_of_beds: {no_of_beds}")
    print(f"latitudes: {latitudes}")
    print(f"longitudes: {longitudes}")
    avg_beds = [appox(beds) for beds in no_of_beds]
    hospital_queue_mat = [return_priority_queue(lat,long,hospital_dict) for lat,long in zip(latitudes,longitudes)]

    for i in range(len(avg_beds)):
        Id_map_accident["accident"+f"{i}"] =  acquire_beds(hospital_queue_mat[i],avg_beds[i],hospital_dict)

    print(Id_map_accident)
    to_alert = []
    for accident,doc in Id_map_accident.items():
        temp_dict = {"hospital_id": doc['h_id'],"mobileNumber": mob.pop(0),"latitude": latitudes.pop(0),"longitude": longitudes.pop(0),"noOfBeds": doc['bed_value']}
        to_alert.append(temp_dict)

    print(to_alert)

    client = MongoClient("mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb")  # Replace <connection_string> with your Atlas URI
    db = client["test"]  # Replace with your database name
    collection = db["alerts"]  # Replace with your collection name
    post_to_mongodb(to_alert,collection)
    return

main_driver()