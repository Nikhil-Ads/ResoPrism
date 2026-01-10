
import pymongo
import datetime
import random

# Connection URI provided by the user
uri = "mongodb+srv://prakharconnects_db_user:qyffHCKVbxxlibwy@cluster0.tgke4r.mongodb.net/?appName=Cluster0"

def verify_connection():
    folder_name = "test_embeddings"
    print(f"Connecting to MongoDB...")
    
    try:
        # Create a new client and connect to the server
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
        # Select database (creating one if it doesn't exist upon first write)
        db = client.test_database
        
        # Select collection
        collection = db.embeddings_test
        
        # Create a dummy embedding (vector of 10 random floats)
        embedding = [random.random() for _ in range(10)]
        
        document = {
            "name": "test_embedding_doc",
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
            "description": "Just checking if things are completing",
            "embedding": embedding
        }
        
        # Insert the document
        result = collection.insert_one(document)
        print(f"Successfully inserted document with _id: {result.inserted_id}")
        print(f"Document content: {document}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    verify_connection()
