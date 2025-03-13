from pymongo import MongoClient

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

# Fetch hospital data
hospital_dict = fetch_hospital_data()

# Print the fetched data
# print("Fetched Hospital Data Dictionary:")
# for hospital_id, data in hospital_dict.items():
#     print(f"Hospital ID: {hospital_id}")
#     print("Data:")
#     for key, value in data.items():
#         print(f"  {key}: {value}")
