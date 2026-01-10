
import os
import pymongo
import hashlib
import datetime
import random
from typing import List
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

def generate_grant_id(title, close_date, sponsor):
    id_str = f"grant|{title}|{close_date or ''}|{sponsor or ''}"
    return hashlib.sha256(id_str.encode()).hexdigest()[:16]

def ingest_grants():
    print("Generating simulated Grant opportunities (Grants.gov)...")
    
    # Realistic Sample Data
    samples = [
        {
            "title": "AI for Early Cancer Detection Research",
            "sponsor": "National Institutes of Health (NIH)",
            "amount": 500000.00,
            "close_date": "2026-06-15",
            "desc": "Funding for innovative AI models to detect early-stage carcinoma from imaging data."
        },
        {
            "title": "Sustainable Energy Storage Systems",
            "sponsor": "Department of Energy (DOE)",
            "amount": 1200000.00,
            "close_date": "2026-04-01",
            "desc": "Grants for next-gen battery technology and grid storage solutions."
        },
        {
            "title": "Machine Learning for Climate Modeling",
            "sponsor": "National Science Foundation (NSF)",
            "amount": 350000.00,
            "close_date": "2026-05-30",
            "desc": "Developing robust ML models to predict extreme weather patterns."
        },
        {
            "title": "Robotics in Surgical Environments",
            "sponsor": "NIH",
            "amount": 750000.00,
            "close_date": "2026-08-20",
            "desc": "Advanced robotics assistance for minimally invasive surgery."
        },
        {
            "title": "Quantum Computing Algorithm Development",
            "sponsor": "DARPA",
            "amount": 2000000.00,
            "close_date": "2026-12-01",
            "desc": "Research into quantum algorithms for cryptography and optimization."
        }
    ]
    
    mongo_docs = []
    
    for item in samples:
        print(f"Processing grant: {item['title']}...")
        
        # Create deterministic ID
        card_id = generate_grant_id(item['title'], item['close_date'], item['sponsor'])
        
        text_to_embed = f"{item['title']}. Sponsor: {item['sponsor']}. {item['desc']}"
        embedding = generate_embedding(text_to_embed)
        
        doc = {
            "id": card_id,
            "type": "grant",
            "title": item['title'],
            "score": round(random.uniform(0.7, 0.99), 2),
            "badge": f"${item['amount']:,.0f}",
            "meta": {
                "close_date": item['close_date'],
                "amount_max": item['amount'],
                "sponsor": item['sponsor'],
                "source": "grants.gov",
                "description": item['desc']
            },
            "embedding": embedding,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        mongo_docs.append(doc)
        
    print(f"Prepared {len(mongo_docs)} grants for storage.")
    
    print("Connecting to MongoDB...")
    client_mongo = pymongo.MongoClient(MONGO_URI)
    db = client_mongo.mongo_research
    collection = db.grants  # storing in 'grants' collection
    
    writes = 0
    for doc in mongo_docs:
        collection.update_one(
            {"id": doc["id"]},
            {"$set": doc},
            upsert=True
        )
        writes += 1
        
    print(f"Successfully upserted {writes} grants into 'mongo_research.grants'.")

if __name__ == "__main__":
    ingest_grants()
