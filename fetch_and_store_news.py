
import requests
import pymongo
import hashlib
import datetime
import random

# Configuration
NEWS_API_KEY = "1843762da0684c908f4bb7cbcd8cf714"
MONGO_URI = "mongodb+srv://prakharconnects_db_user:hackathon2024@cluster0.tgke4r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

def generate_news_id(title, published_date, outlet):
    """Generate deterministic ID matching the logic in models.py"""
    id_str = f"news|{title}|{published_date or ''}|{outlet or ''}"
    return hashlib.sha256(id_str.encode()).hexdigest()[:16]

def fetch_and_store():
    print("Fetching news from NewsAPI...")
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
            source_name = article.get("source", {}).get("name")
            published_at = article.get("publishedAt")
            url = article.get("url")
            
            if not title:
                continue
                
            # Create deterministic ID
            card_id = generate_news_id(title, published_at, source_name)
            
            # Simple score simulation (since we don't have the ranker yet)
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
                    "source": "newsapi"
                },
                "created_at": datetime.datetime.utcnow()
            }
            mongo_docs.append(doc)
            
        if not mongo_docs:
            print("No valid articles to store.")
            return

        print(f"Prepared {len(mongo_docs)} documents for storage.")
        
        print("Connecting to MongoDB...")
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Ping to check connection before inserting
        client.admin.command('ping')
        print("MongoDB connection successful.")
        
        db = client.test_database
        collection = db.news_articles
        
        # Using insert_many for efficiency
        # We might want to use update_one with upsert=True in a real app to avoid duplicates, 
        # but for this test insert_many is fine (or ordered=False to skip duplicates if _id was set as Mongo ID)
        # Here we are generating a custom 'id' field, but Mongo uses '_id'.
        # Let's set '_id' to our custom 'id' to prevent duplicates naturally.
        for doc in mongo_docs:
            doc['_id'] = doc['id']
            
        try:
            result = collection.insert_many(mongo_docs, ordered=False)
            print(f"Successfully inserted {len(result.inserted_ids)} articles.")
        except pymongo.errors.BulkWriteError as bwe:
            print(f"Inserted some articles, but encountered duplicates/errors: {bwe.details['nInserted']} inserted.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
    except pymongo.errors.OperationFailure as e:
        print(f"MongoDB Authentication/Operation failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_and_store()
