
import os
import requests
import pymongo
import hashlib
import datetime
import random
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai

# 1. Environment Setup
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not all([MONGO_URI, OPENAI_API_KEY, NEWS_API_KEY]):
    raise ValueError("Missing API Keys (MONGO_URI, OPENAI_API_KEY, NEWS_API_KEY) in .env file")

client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)
client_mongo = pymongo.MongoClient(MONGO_URI)
db = client_mongo.mongo_research

# 2. Helper Functions
def generate_embedding(text: str) -> List[float]:
    """Generates a vector embedding using OpenAI."""
    try:
        text = text.replace("\n", " ").strip()
        if not text: return []
        resp = client_openai.embeddings.create(input=[text], model="text-embedding-3-small")
        return resp.data[0].embedding
    except Exception as e:
        print(f"  [X] Embedding error: {e}")
        return []

def get_deterministic_id(prefix: str, *parts) -> str:
    """Creates a consistent ID based on content."""
    raw = f"{prefix}|" + "|".join([str(p) for p in parts])
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def upsert_to_mongo(collection_name: str, docs: List[Dict]):
    """Stores documents in MongoDB with upsert behavior."""
    if not docs:
        print(f"  [!] No documents to ingest for {collection_name}.")
        return
        
    collection = db[collection_name]
    writes = 0
    for doc in docs:
        try:
            collection.update_one(
                {"id": doc["id"]},
                {"$set": doc},
                upsert=True
            )
            writes += 1
        except Exception as e:
            print(f"  [X] DB Write Error: {e}")
            
    print(f"  [✓] Successfully stored/updated {writes} items in '{collection_name}' collection.")

# 3. Data Ingestion Functions

def process_news():
    print("\n--- Processing NEWS Data ---")
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=science&pageSize=100&apiKey={NEWS_API_KEY}"
    
    try:
        resp = requests.get(url)
        data = resp.json()
        articles = data.get("articles", [])
        print(f"  [i] Found {len(articles)} articles from NewsAPI.")
        
        mongo_docs = []
        for art in articles:
            title = art.get("title")
            if not title or title == "[Removed]": continue
            
            # Embed: Title + Description
            text_to_embed = f"{title}. {art.get('description') or ''}"
            embedding = generate_embedding(text_to_embed)
            
            card_id = get_deterministic_id("news", title, art.get("publishedAt"))
            
            doc = {
                "id": card_id,
                "type": "news",
                "title": title,
                "embedding": embedding,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
                "score": round(random.uniform(0.5, 0.9), 2), # Simulated relevance baseline
                "meta": {
                    "source": "newsapi",
                    "outlet": art.get("source", {}).get("name"),
                    "url": art.get("url"),
                    "published_at": art.get("publishedAt"),
                    "description": art.get("description")
                }
            }
            mongo_docs.append(doc)
            
        upsert_to_mongo("news", mongo_docs)

    except Exception as e:
        print(f"  [X] News processing failed: {e}")

def process_papers(topic="artificial intelligence medical"):
    print(f"\n--- Processing PAPERS Data (Topic: {topic}) ---")
    
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    try:
        # 1. Get IDs
        params = {"db": "pubmed", "term": topic, "retmode": "json", "retmax": 60}
        r1 = requests.get(search_url, params=params)
        id_list = r1.json().get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            print("  [!] No papers found.")
            return

        # 2. Get Details
        r2 = requests.get(summary_url, params={"db": "pubmed", "id": ",".join(id_list), "retmode": "json"})
        results = r2.json().get("result", {})
        results.pop("uids", None)
        
        mongo_docs = []
        for uid, item in results.items():
            title = item.get("title", "")
            if not title: continue
            
            authors = [a.get("name") for a in item.get("authors", [])]
            authors_str = ", ".join(authors[:3])
            
            # Embed: Title + Authors + Journal
            text_to_embed = f"{title}. {authors_str}. {item.get('source')}"
            embedding = generate_embedding(text_to_embed)
            
            card_id = get_deterministic_id("paper", title, uid)
            
            doc = {
                "id": card_id,
                "type": "paper",
                "title": title,
                "embedding": embedding,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
                "score": round(random.uniform(0.6, 0.95), 2),
                "meta": {
                    "source": item.get("source"),
                    "authors": authors,
                    "published_date": item.get("pubdate"),
                    "pubmed_id": uid,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
                }
            }
            mongo_docs.append(doc)
            time.sleep(0.5) # Rate limit kindness
            
        upsert_to_mongo("papers", mongo_docs)
        
    except Exception as e:
        print(f"  [X] Papers processing failed: {e}")

def process_grants(keyword="Artificial Intelligence"):
    print(f"\n--- Processing GRANTS Data (NSF API: '{keyword}') ---")
    
    url = "https://api.nsf.gov/services/v1/awards.json"
    params = {
        "keyword": keyword,
        "printFields": "id,title,fundsObligatedAmt,awardeeName,date,abstractText",
        "offset": 0,
        "rpp": 75  # Top 75 grants
    }
    
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        # NSF API structure: {"response": {"award": [...] }}
        awards = data.get("response", {}).get("award", [])
        
        if not awards:
            print("  [!] No grants found.")
            return

        print(f"  [i] Found {len(awards)} grants from NSF.")
        
        mongo_docs = []
        for item in awards:
            title = item.get("title")
            sponsor = item.get("awardeeName")
            desc = item.get("abstractText") or ""
            amount_str = item.get("fundsObligatedAmt")
            
            # Clean amount (e.g., "500000")
            try:
                amount = float(amount_str) if amount_str else 0.0
            except:
                amount = 0.0
            
            # Embed: Title + Awardee + Abstract
            text_to_embed = f"{title}. Sponsor: {sponsor}. {desc}"
            embedding = generate_embedding(text_to_embed)
            
            card_id = get_deterministic_id("grant", title, item.get("id"))
            
            doc = {
                "id": card_id,
                "type": "grant",
                "title": title,
                "embedding": embedding,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
                "score": round(random.uniform(0.7, 0.99), 2),
                "meta": {
                    "source": "nsf.gov",
                    "sponsor": sponsor,
                    "amount_max": amount,
                    "description": desc[:500] + "...", # Truncate long abstracts
                    "date": item.get("date"),
                    "external_id": item.get("id")
                }
            }
            mongo_docs.append(doc)
            time.sleep(0.2)
        
        upsert_to_mongo("grants", mongo_docs)
        
    except Exception as e:
        print(f"  [X] Grants processing failed: {e}")

# 4. Main Execution
if __name__ == "__main__":
    print("🚀 Starting Unified Data Pipeline...")
    process_news()
    process_papers()
    process_grants()
    print("\n✅ Pipeline Complete. Data is ready in MongoDB.")
