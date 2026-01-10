
import os
import pymongo
from typing import List, Dict
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([MONGO_URI, OPENAI_API_KEY]):
    raise ValueError("Missing keys in .env")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_embedding(text: str) -> List[float]:
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def search_collection(collection, query_embedding, limit=3):
    """Generic search function for any collection with a 'vector_index'."""
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 50,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "type": 1,
                "score": { "$meta": "vectorSearchScore" },
                "meta": 1
            }
        }
    ]
    try:
        return list(collection.aggregate(pipeline))
    except pymongo.errors.OperationFailure as e:
        print(f"  [!] Search failed for collection '{collection.name}': {e}")
        return []

def orchestrator_search(query: str):
    print(f"\n--- Orchestrator Search: '{query}' ---\n")
    print("1. Generating Query Embedding...")
    query_embedding = generate_embedding(query)
    
    print("2. Connecting to MongoDB...")
    client_mongo = pymongo.MongoClient(MONGO_URI)
    db = client_mongo.mongo_research
    
    # 3. Parallel Search (simulated)
    collections = ["news", "papers", "grants"]
    all_results = []
    
    for col_name in collections:
        print(f"   > Searching '{col_name}' collection...")
        results = search_collection(db[col_name], query_embedding)
        all_results.extend(results)
        
    # 4. Rank / Sort by Score
    print("3. Ranking combined results...")
    all_results.sort(key=lambda x: x['score'], reverse=True)
    
    # 5. Display
    print(f"\nTotal Found: {len(all_results)} items.\n")
    print("--- FINAL BRIEF ---\n")
    
    for i, item in enumerate(all_results[:5], 1): # Top 5 mixed
        kind = item.get('type', 'unknown').upper()
        title = item.get('title')
        score = item.get('score')
        
        print(f"{i}. [{kind}] {title}")
        print(f"   Relevance: {score:.4f}")
        if kind == 'GRANT':
            print(f"   Sponsor: {item['meta'].get('sponsor')} | {item['meta'].get('amount_max')}")
        elif kind == 'PAPER':
            print(f"   Journal: {item['meta'].get('source')}")
        elif kind == 'NEWS':
            print(f"   Source: {item['meta'].get('outlet')}")
        print()

if __name__ == "__main__":
    # Test queries
    orchestrator_search("Funding for artificial intelligence in medicine")
