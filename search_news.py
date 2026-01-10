
import os
import pymongo
from typing import List
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([MONGO_URI, OPENAI_API_KEY]):
    raise ValueError("Missing API keys in .env file")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI's text-embedding-3-small model."""
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def search_news(query: str):
    print(f"Generating embedding for query: '{query}'")
    query_embedding = generate_embedding(query)
    
    print("Connecting to MongoDB...")
    client_mongo = pymongo.MongoClient(MONGO_URI)
    db = client_mongo.mongo_research
    collection = db.news
    
    # Vector Search Pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",  # User must create this index in Atlas
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": 5
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "score": { "$meta": "vectorSearchScore" },
                "meta": 1
            }
        }
    ]
    
    print("Executing Vector Search...")
    try:
        results = list(collection.aggregate(pipeline))
        
        if not results:
            print("No results found. Did you create the Atlas Search Index?")
        else:
            print(f"\nFound {len(results)} relevant articles:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   Score: {result['score']:.4f}")
                print(f"   Source: {result['meta'].get('outlet')}")
                print(f"   URL: {result['meta'].get('url')}\n")
                
    except pymongo.errors.OperationFailure as e:
        print(f"Search failed: {e}")
        print("Note: Ensure you have created a Vector Search Index named 'vector_index' in Atlas.")

if __name__ == "__main__":
    current_query = "New discoveries in space exploration" # Example query
    search_news(current_query)
