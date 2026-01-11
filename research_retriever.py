import os
import pymongo
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class ResearchRetriever:
    def __init__(self):
        """
        Initialize the retriever with MongoDB and OpenAI clients.
        """
        # Try both MONGO_URI and MONGODB_URI for compatibility
        self.mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not all([self.mongo_uri, self.openai_api_key]):
            raise ValueError("Missing MONGO_URI (or MONGODB_URI) or OPENAI_API_KEY in .env")
        
        # Validate MongoDB URI format (basic check)
        if not (self.mongo_uri.startswith("mongodb://") or self.mongo_uri.startswith("mongodb+srv://")):
            raise ValueError(f"Invalid MongoDB URI format. Must start with 'mongodb://' or 'mongodb+srv://'. Got: {self.mongo_uri[:20]}...")
            
        self.client_openai = openai.OpenAI(api_key=self.openai_api_key)
        
        # Connect to MongoDB with server selection timeout
        try:
            self.client_mongo = pymongo.MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Test the connection
            self.client_mongo.admin.command('ping')
            self.db = self.client_mongo.mongo_research
        except pymongo.errors.ServerSelectionTimeoutError as e:
            raise ConnectionError(f"MongoDB connection timeout. Check your connection string and network: {str(e)}")
        except pymongo.errors.OperationFailure as e:
            # This is the authentication error we're seeing
            error_msg = str(e)
            if "Authentication failed" in error_msg:
                raise ValueError(
                    f"MongoDB authentication failed. Please check:\n"
                    f"1. Username and password in connection string\n"
                    f"2. Database user permissions\n"
                    f"3. Connection string format: mongodb://username:password@host:port/database\n"
                    f"Error: {error_msg}"
                )
            else:
                raise
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
        
    def _generate_embedding(self, text: str) -> List[float]:
        """Internal helper to generate vector embeddings."""
        text = text.replace("\n", " ").strip()
        resp = self.client_openai.embeddings.create(
            input=[text], 
            model="text-embedding-3-small"
        )
        return resp.data[0].embedding

    def _vector_search(self, collection_name: str, query: str, limit: int = 3) -> List[Dict]:
        """
        Generic vector search for any collection.
        """
        print(f"  [Retriever] Generating embedding for query: '{query}'...")
        query_vector = self._generate_embedding(query)
        
        collection = self.db[collection_name]
        
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 50,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "title": 1,
                    "score": { "$meta": "vectorSearchScore" },
                    "meta": 1,
                    "type": 1
                }
            }
        ]
        
        print(f"  [Retriever] Searching '{collection_name}' collection...")
        try:
            results = list(collection.aggregate(pipeline))
            return results
        except pymongo.errors.OperationFailure as e:
            error_msg = str(e)
            if "Authentication failed" in error_msg or "code" in error_msg and "18" in error_msg:
                raise ValueError(
                    f"MongoDB authentication failed during query. Please check:\n"
                    f"1. Username and password in your MONGO_URI connection string\n"
                    f"2. URL-encode special characters in password (e.g., @ becomes %40)\n"
                    f"3. Ensure the database user has read permissions on 'mongo_research' database\n"
                    f"4. Connection string format should be: mongodb+srv://username:password@cluster.mongodb.net/database\n"
                    f"   or: mongodb://username:password@host:port/database\n"
                    f"Error details: {error_msg}"
                )
            else:
                raise

    # --- Public Methods for Teammates' Agents ---

    def search_news(self, query: str, limit=5) -> List[Dict]:
        """Call this from your News Agent"""
        return self._vector_search("news", query, limit)

    def search_papers(self, query: str, limit=5) -> List[Dict]:
        """Call this from your Papers Agent"""
        return self._vector_search("papers", query, limit)

    def search_grants(self, query: str, limit=5) -> List[Dict]:
        """Call this from your Grants Agent"""
        return self._vector_search("grants", query, limit)

# Example Usage
if __name__ == "__main__":
    retriever = ResearchRetriever()
    
    # Example 1: News Agent asks for help
    print("\n--- News Agent Query ---")
    news = retriever.search_news("Recent breakthroughs in AI", limit=2)
    for item in news:
        print(f"[News] {item['title']} (Score: {item['score']:.2f})")

    # Example 2: Grants Agent asks for help
    print("\n--- Grants Agent Query ---")
    grants = retriever.search_grants("Funding for cancer research", limit=2)
    for item in grants:
        print(f"[Grant] {item['title']} (Score: {item['score']:.2f})")