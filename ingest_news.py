
import os
import requests
import pymongo
import hashlib
import datetime
import random
from typing import List, Optional
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([NEWS_API_KEY, MONGO_URI, OPENAI_API_KEY]):
    raise ValueError("Missing API keys in .env file")

# Initialize OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&category=science&apiKey={NEWS_API_KEY}"

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI's text-embedding-3-small model."""
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def generate_news_id(title, published_date, outlet):
    """Generate deterministic ID matching the logic in models.py"""
    id_str = f"news|{title}|{published_date or ''}|{outlet or ''}"
    return hashlib.sha256(id_str.encode()).hexdigest()[:16]

def ingest_news():
    print("Fetching news from NewsAPI (Category: Science)...")
    try:
        response = requests.get(NEWS_URL)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get("articles", [])
        print(f"Found {len(articles)} articles.")
        
        mongo_docs = []
        for article in articles:
            # Map NewsAPI data to our schema
            title = article.get("title")
            description = article.get("description") or ""
            content = article.get("content") or ""
            source_name = article.get("source", {}).get("name")
            published_at = article.get("publishedAt")
            url = article.get("url")
            
            if not title:
                continue
                
            # Create deterministic ID
            card_id = generate_news_id(title, published_at, source_name)
            
            # Combine text for embedding
            text_to_embed = f"{title}. {description}"
            
            print(f"Generating embedding for: {title[:30]}...")
            embedding = generate_embedding(text_to_embed)
            
            # Simple score simulation
            score = round(random.uniform(0.5, 0.9), 2)
            
            doc = {
                "id": card_id,
                "type": "news",
                "title": title,
                "score": score,
                "badge": "Breaking" if score > 0.8 else None,
                "meta": {
                    "published_date": published_at,
                    "outlet": source_name,
                    "url": url,
                    "source": "newsapi",
                    "description": description
                },
                "embedding": embedding,
                "created_at": datetime.datetime.now(datetime.timezone.utc)
            }
            mongo_docs.append(doc)
            
        if not mongo_docs:
            print("No valid articles to store.")
            return

        print(f"Prepared {len(mongo_docs)} documents with embeddings.")
        
        print("Connecting to MongoDB...")
        client_mongo = pymongo.MongoClient(MONGO_URI)
        db = client_mongo.mongo_research  # Using a proper database name 'mongo_research'
        collection = db.news
        
        # Upsert documents
        writes = 0
        for doc in mongo_docs:
            # Upsert based on 'id'
            collection.update_one(
                {"id": doc["id"]},
                {"$set": doc},
                upsert=True
            )
            writes += 1
            
        print(f"Successfully upserted {writes} articles into 'mongo_research.news'.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    ingest_news()
