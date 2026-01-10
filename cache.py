"""MongoDB caching module for URL research results."""

import os
import hashlib
import logging
import sys
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError, OperationFailure, ConfigurationError, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Track MongoDB connection status and last error
_mongodb_status = {
    "connected": False,
    "last_error": None,
    "error_details": None,
    "diagnostics": None
}


# Global MongoDB client (initialized on first use)
_mongo_client: Optional[MongoClient] = None
_db = None


def _parse_mongodb_error(error: Exception) -> Tuple[str, str]:
    """
    Parse MongoDB error and provide detailed diagnostic information.
    
    Returns:
        Tuple of (error_type, detailed_message)
    """
    error_msg = str(error)
    error_type = type(error).__name__
    detailed_msg = []
    
    # Authentication errors
    if "Authentication failed" in error_msg or isinstance(error, OperationFailure):
        if "code" in dir(error) and error.code == 18:  # AuthenticationFailed
            detailed_msg.append("❌ AUTHENTICATION FAILED")
            detailed_msg.append("")
            detailed_msg.append("The MongoDB credentials in your connection string are incorrect or the user doesn't have permissions.")
            detailed_msg.append("")
            detailed_msg.append("Possible fixes:")
            detailed_msg.append("  1. Check your username and password in MONGODB_URI")
            detailed_msg.append("  2. Verify the database user exists in MongoDB Atlas")
            detailed_msg.append("  3. Ensure the user has read/write permissions on the database")
            detailed_msg.append("  4. Check if you need to specify a database name in the URI path")
            detailed_msg.append("     Example: mongodb+srv://user:pass@cluster.mongodb.net/dbname?options")
    
    # Connection timeout errors
    elif isinstance(error, (ConnectionFailure, ServerSelectionTimeoutError)):
        detailed_msg.append("❌ CONNECTION TIMEOUT")
        detailed_msg.append("")
        detailed_msg.append("Cannot reach the MongoDB server.")
        detailed_msg.append("")
        detailed_msg.append("Possible fixes:")
        detailed_msg.append("  1. Check your internet connection")
        detailed_msg.append("  2. Verify the MongoDB cluster URL is correct")
        detailed_msg.append("  3. Check if your IP address is whitelisted in MongoDB Atlas Network Access")
        detailed_msg.append("  4. For MongoDB Atlas, allow '0.0.0.0/0' (all IPs) if unsure, or add your specific IP")
    
    # Configuration errors
    elif isinstance(error, ConfigurationError):
        detailed_msg.append("❌ CONFIGURATION ERROR")
        detailed_msg.append("")
        detailed_msg.append("The MongoDB connection string format is incorrect.")
        detailed_msg.append("")
        detailed_msg.append("Possible fixes:")
        detailed_msg.append("  1. Check MONGODB_URI format: mongodb+srv://user:pass@cluster.mongodb.net/dbname")
        detailed_msg.append("  2. Ensure special characters in password are URL-encoded")
        detailed_msg.append("  3. Verify the URI doesn't have extra spaces or invalid characters")
    
    # Generic errors
    else:
        detailed_msg.append(f"❌ ERROR: {error_type}")
        detailed_msg.append("")
        detailed_msg.append(f"Error message: {error_msg}")
        detailed_msg.append("")
        detailed_msg.append("Check your MongoDB connection string and network settings.")
    
    detailed_msg.append("")
    detailed_msg.append(f"Full error: {error_msg}")
    
    return error_type, "\n".join(detailed_msg)


def _get_mongo_client() -> Optional[MongoClient]:
    """Get or create MongoDB client."""
    global _mongo_client, _db, _mongodb_status
    
    if _mongo_client is not None:
        return _mongo_client
    
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DB_NAME", "mongo_research")
    
    # Parse URI for diagnostics
    uri_info = "Unknown"
    if mongodb_uri.startswith("mongodb+srv://"):
        try:
            # Extract cluster info
            parts = mongodb_uri.split("@")
            if len(parts) > 1:
                cluster_part = parts[1].split("/")[0].split("?")[0]
                uri_info = f"MongoDB Atlas cluster: {cluster_part}"
        except:
            pass
    
    try:
        _mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        # Test connection
        _mongo_client.admin.command("ping")
        _db = _mongo_client[db_name]
        
        # Verify write access by attempting a test operation
        test_collection = _db["_test_connection"]
        test_collection.insert_one({"_test": True, "timestamp": datetime.utcnow()})
        test_collection.delete_one({"_test": True})
        
        logger.info(f"✓ Connected to MongoDB: {db_name} ({uri_info})")
        _mongodb_status["connected"] = True
        _mongodb_status["last_error"] = None
        _mongodb_status["error_details"] = None
        
        return _mongo_client
        
    except OperationFailure as e:
        error_type, detailed_msg = _parse_mongodb_error(e)
        _mongodb_status["connected"] = False
        _mongodb_status["last_error"] = error_type
        _mongodb_status["error_details"] = detailed_msg
        _mongodb_status["diagnostics"] = {
            "uri_info": uri_info,
            "db_name": db_name,
            "error_code": getattr(e, 'code', None)
        }
        
        logger.error(f"MongoDB Authentication/Operation Error:\n{detailed_msg}")
        logger.warning("⚠️  MongoDB caching is DISABLED. Results will not be persisted.")
        
        _mongo_client = None
        _db = None
        return None
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        error_type, detailed_msg = _parse_mongodb_error(e)
        _mongodb_status["connected"] = False
        _mongodb_status["last_error"] = error_type
        _mongodb_status["error_details"] = detailed_msg
        _mongodb_status["diagnostics"] = {
            "uri_info": uri_info,
            "db_name": db_name
        }
        
        logger.error(f"MongoDB Connection Error:\n{detailed_msg}")
        logger.warning("⚠️  MongoDB caching is DISABLED. Results will not be persisted.")
        
        _mongo_client = None
        _db = None
        return None
        
    except ConfigurationError as e:
        error_type, detailed_msg = _parse_mongodb_error(e)
        _mongodb_status["connected"] = False
        _mongodb_status["last_error"] = error_type
        _mongodb_status["error_details"] = detailed_msg
        
        logger.error(f"MongoDB Configuration Error:\n{detailed_msg}")
        logger.warning("⚠️  MongoDB caching is DISABLED. Results will not be persisted.")
        
        _mongo_client = None
        _db = None
        return None
        
    except Exception as e:
        error_type, detailed_msg = _parse_mongodb_error(e)
        _mongodb_status["connected"] = False
        _mongodb_status["last_error"] = error_type
        _mongodb_status["error_details"] = detailed_msg
        
        logger.error(f"MongoDB Error ({type(e).__name__}):\n{detailed_msg}")
        logger.warning("⚠️  MongoDB caching is DISABLED. Results will not be persisted.")
        
        _mongo_client = None
        _db = None
        return None


def _get_collection():
    """Get the cache collection."""
    global _db
    
    if _db is None:
        client = _get_mongo_client()
        if client is None:
            return None
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGODB_DB_NAME", "mongo_research")
        _db = client[db_name]
    
    return _db.get_collection("url_research_cache")


def _url_to_hash(url: str) -> str:
    """Convert URL to a hash for use as document ID."""
    # Normalize URL (remove trailing slash, convert to lowercase)
    normalized_url = url.strip().rstrip("/").lower()
    return hashlib.sha256(normalized_url.encode()).hexdigest()


def get_cached_results(url: str) -> Optional[Dict[str, Any]]:
    """
    Get cached research results for a URL.
    
    Args:
        url: The URL to look up in cache
        
    Returns:
        Cached results dictionary or None if not found
    """
    try:
        collection = _get_collection()
        if collection is None:
            return None
        
        url_hash = _url_to_hash(url)
        cached_doc = collection.find_one({"_id": url_hash})
        
        if cached_doc:
            logger.info(f"Cache hit for URL: {url}")
            # Remove MongoDB _id from returned dict
            cached_doc.pop("_id", None)
            return cached_doc
        else:
            logger.info(f"Cache miss for URL: {url}")
            return None
            
    except OperationFailure as e:
        error_type, detailed_msg = _parse_mongodb_error(e)
        logger.error(f"❌ MongoDB operation error while getting cache:")
        logger.error(detailed_msg)
        return None
    except PyMongoError as e:
        error_type, detailed_msg = _parse_mongodb_error(e)
        logger.error(f"❌ MongoDB error while getting cache:")
        logger.error(detailed_msg)
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error getting cached results: {type(e).__name__}: {str(e)}")
        return None


def get_mongodb_status() -> Dict[str, Any]:
    """
    Get current MongoDB connection status and diagnostics.
    
    Returns:
        Dictionary with connection status, error details, and diagnostics
    """
    global _mongodb_status
    
    # If we haven't tried to connect yet, attempt it now
    if _mongodb_status.get("diagnostics") is None:
        _get_mongo_client()
    
    return {
        "connected": _mongodb_status["connected"],
        "last_error": _mongodb_status["last_error"],
        "error_details": _mongodb_status["error_details"],
        "diagnostics": _mongodb_status.get("diagnostics", {}),
        "mongodb_uri_set": bool(os.getenv("MONGODB_URI")),
        "db_name": os.getenv("MONGODB_DB_NAME", "mongo_research")
    }


def save_to_cache(url: str, keywords: list[str], grants: list, papers: list, news: list) -> bool:
    """
    Save research results to MongoDB cache.
    Stores results in:
    1. url_research_cache collection (aggregated cache by URL)
    2. papers collection (individual papers with lab URL reference)
    3. news collection (individual news articles with lab URL reference)
    4. grants collection (individual grants with lab URL reference)
    
    Args:
        url: The original URL
        keywords: List of extracted keywords
        grants: List of GrantCard objects (will be serialized)
        papers: List of PaperCard objects (will be serialized)
        news: List of NewsCard objects (will be serialized)
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        collection = _get_collection()
        if collection is None:
            status = get_mongodb_status()
            if not status["connected"] and status["error_details"]:
                logger.warning("❌ MongoDB not available - cache save skipped")
                logger.info("MongoDB Diagnostics:\n" + status["error_details"])
            else:
                logger.warning("MongoDB not available, skipping cache save")
            return False
        
        # Get database reference
        db = collection.database
        
        url_hash = _url_to_hash(url)
        now = datetime.utcnow()
        
        # Convert Pydantic models to dict for storage
        grants_dict = [grant.model_dump() if hasattr(grant, "model_dump") else grant for grant in grants]
        papers_dict = [paper.model_dump() if hasattr(paper, "model_dump") else paper for paper in papers]
        news_dict = [news_item.model_dump() if hasattr(news_item, "model_dump") else news_item for news_item in news]
        
        # 1. Save to cache collection (aggregated by URL)
        cache_doc = {
            "_id": url_hash,
            "url": url,
            "keywords": keywords,
            "grants": grants_dict,
            "papers": papers_dict,
            "news": news_dict,
            "created_at": now,
            "updated_at": now,
        }
        
        collection.replace_one(
            {"_id": url_hash},
            cache_doc,
            upsert=True
        )
        
        logger.info(f"Cached aggregated results for URL: {url}")
        
        # 2. Store papers in separate collection with lab URL reference
        papers_collection = db.get_collection("papers")
        papers_saved = 0
        for paper in papers_dict:
            try:
                paper_doc = {
                    "_id": paper.get("id"),  # Use paper's ID as document ID
                    "paper_data": paper,
                    "lab_url": url,
                    "lab_url_hash": url_hash,
                    "keywords": keywords,
                    "created_at": now,
                    "updated_at": now,
                }
                papers_collection.replace_one(
                    {"_id": paper.get("id")},
                    paper_doc,
                    upsert=True
                )
                papers_saved += 1
            except Exception as e:
                logger.warning(f"Error saving paper {paper.get('id', 'unknown')}: {str(e)}")
                continue
        
        if papers_saved > 0:
            logger.info(f"Saved {papers_saved} papers to papers collection")
        
        # 3. Store news articles in separate collection with lab URL reference
        news_collection = db.get_collection("news")
        news_saved = 0
        for news_item in news_dict:
            try:
                news_doc = {
                    "_id": news_item.get("id"),  # Use news item's ID as document ID
                    "news_data": news_item,
                    "lab_url": url,
                    "lab_url_hash": url_hash,
                    "keywords": keywords,
                    "created_at": now,
                    "updated_at": now,
                }
                news_collection.replace_one(
                    {"_id": news_item.get("id")},
                    news_doc,
                    upsert=True
                )
                news_saved += 1
            except Exception as e:
                logger.warning(f"Error saving news {news_item.get('id', 'unknown')}: {str(e)}")
                continue
        
        if news_saved > 0:
            logger.info(f"Saved {news_saved} news articles to news collection")
        
        # 4. Store grants in separate collection with lab URL reference
        grants_collection = db.get_collection("grants")
        grants_saved = 0
        for grant in grants_dict:
            try:
                grant_doc = {
                    "_id": grant.get("id"),  # Use grant's ID as document ID
                    "grant_data": grant,
                    "lab_url": url,
                    "lab_url_hash": url_hash,
                    "keywords": keywords,
                    "created_at": now,
                    "updated_at": now,
                }
                grants_collection.replace_one(
                    {"_id": grant.get("id")},
                    grant_doc,
                    upsert=True
                )
                grants_saved += 1
            except Exception as e:
                logger.warning(f"Error saving grant {grant.get('id', 'unknown')}: {str(e)}")
                continue
        
        if grants_saved > 0:
            logger.info(f"Saved {grants_saved} grants to grants collection")
        
        # Create indexes for better querying
        try:
            papers_collection.create_index("lab_url_hash")
            papers_collection.create_index("lab_url")
            news_collection.create_index("lab_url_hash")
            news_collection.create_index("lab_url")
            grants_collection.create_index("lab_url_hash")
            grants_collection.create_index("lab_url")
            logger.info("Created indexes for lab_url_hash and lab_url")
        except Exception as e:
            logger.warning(f"Error creating indexes (may already exist): {str(e)}")
        
        logger.info(f"✅ Successfully cached all results for URL: {url}")
        logger.info(f"   - {papers_saved} papers stored in papers collection")
        logger.info(f"   - {news_saved} news articles stored in news collection")
        logger.info(f"   - {grants_saved} grants stored in grants collection")
        
        return True
        
    except OperationFailure as e:
        error_type, detailed_msg = _parse_mongodb_error(e)
        logger.error(f"❌ MongoDB operation error while saving cache:")
        logger.error(detailed_msg)
        logger.error(f"Failed to save cache for URL: {url}")
        return False
    except PyMongoError as e:
        error_type, detailed_msg = _parse_mongodb_error(e)
        logger.error(f"❌ MongoDB error while saving cache:")
        logger.error(detailed_msg)
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error saving to cache: {type(e).__name__}: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def clear_cache(url: Optional[str] = None) -> bool:
    """
    Clear cache for a specific URL or all cache entries.
    
    Args:
        url: URL to clear (if None, clears all cache)
        
    Returns:
        True if cleared successfully, False otherwise
    """
    try:
        collection = _get_collection()
        if collection is None:
            return False
        
        if url:
            url_hash = _url_to_hash(url)
            result = collection.delete_one({"_id": url_hash})
            logger.info(f"Cleared cache for URL: {url}")
            return result.deleted_count > 0
        else:
            result = collection.delete_many({})
            logger.info(f"Cleared all cache entries: {result.deleted_count} documents")
            return True
            
    except PyMongoError as e:
        logger.warning(f"MongoDB error while clearing cache: {str(e)}")
        return False
    except Exception as e:
        logger.warning(f"Error clearing cache: {str(e)}")
        return False
