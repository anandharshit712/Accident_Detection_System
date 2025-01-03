from pymongo import MongoClient


def fetch_user_data():

    max_documents_per_user = 5
    connection_string = "mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb"
    database_name = "test"
    collection_name = "sensordatas"

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

        return user_data_dict
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


# # Fetch user data
# user_data = fetch_user_data()
#
# # Print the fetched data
# print("Fetched Data Dictionary:")
# for mobile_number, documents in user_data.items():
#     print(f"Mobile Number: {mobile_number}")
#     print("Data:")
#     for doc in documents:
#         print(doc)
