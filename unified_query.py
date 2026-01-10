
import os
import sys
import pymongo
from typing import List
from dotenv import load_dotenv
import openai
import argparse

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([MONGO_URI, OPENAI_API_KEY]):
    print("Error: Missing MONGO_URI or OPENAI_API_KEY in .env file.")
    sys.exit(1)

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI's text-embedding-3-small model."""
    try:
        text = text.replace("\n", " ")
        return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

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
        # Gracefully handle missing index or collection issues
        # print(f"  [!] Search failed for collection '{collection.name}': {e}") 
        return []

def query_research_assistant(query: str):
    print(f"\nResearch Assistant Query: '{query}'\n" + "="*50)
    
    print("1. Understanding query (Generating Embedding)...")
    query_embedding = generate_embedding(query)
    if not query_embedding:
        print("Failed to generate embedding.")
        return

    print("2. Connecting to MongoDB Atlas...")
    try:
        client_mongo = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client_mongo.mongo_research
    except Exception as e:
        print(f"Connection failed: {e}")
        return
    
    # 3. Parallel Search
    print("3. Searching Knowledge Base (News, Papers, Grants)...")
    collections = ["news", "papers", "grants"]
    all_results = []
    
    for col_name in collections:
        results = search_collection(db[col_name], query_embedding)
        all_results.extend(results)
        print(f"   - Found {len(results)} matches in '{col_name}'")

    if not all_results:
        print("\nNo results found. Ensure you have ingested data and created 'vector_index' on all collections.")
        return

    # 4. Rank / Sort by Score
    print("4. Ranking and Unifying Results...")
    all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # 5. Display
    print("\n" + "="*50)
    print(f"TOP RESULTS FOR: '{query}'")
    print("="*50 + "\n")
    
    for i, item in enumerate(all_results[:10], 1): # Show Top 10
        kind = item.get('type', 'unknown').upper()
        title = item.get('title')
        score = item.get('score', 0)
        
        # Color coding simulation (terminal friendly)
        
        print(f"{i}. [{kind}] {title}")
        print(f"   Relevance: {score:.1%}")
        
        if kind == 'GRANT':
            amount = item.get('meta', {}).get('amount_max', 0)
            sponsor = item.get('meta', {}).get('sponsor', 'N/A')
            print(f"   Details: {sponsor} | ${amount:,.2f}")
        elif kind == 'PAPER':
            journal = item.get('meta', {}).get('source', 'N/A')
            authors = item.get('meta', {}).get('authors', [])
            auth_str = ", ".join(authors[:2]) + ("..." if len(authors) > 2 else "")
            print(f"   Details: {journal} | {auth_str}")
        elif kind == 'NEWS':
            outlet = item.get('meta', {}).get('outlet', 'N/A')
            print(f"   Details: {outlet}")
            
        url = item.get('meta', {}).get('url') or item.get('meta', {}).get('link')
        if url:
            print(f"   Link: {url}")
        print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        # Default query if none provided
        user_query = "AI in medical research and funding"
        
    query_research_assistant(user_query)
