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

    query = {'mobileNumber': '9661083779'}

    # Fetch data from the collection
    documents = collection.find(query)

    # Convert the documents to a list and return
    return list(documents)

# Example usage
docs = fetch_documents_from_mongodb()
for doc in docs:
    print(doc)
