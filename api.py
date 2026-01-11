"""FastAPI server for Research Inbox Orchestrator."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from orchestrator import ORCHESTRATOR
from models import ResearchState
try:
    from url_research_service import process_url_research
    URL_RESEARCH_AVAILABLE = True
except ImportError as e:
    URL_RESEARCH_AVAILABLE = False
    URL_RESEARCH_ERROR = str(e)
    
try:
    from cache import get_mongodb_status
    MONGODB_STATUS_AVAILABLE = True
except ImportError:
    MONGODB_STATUS_AVAILABLE = False
    
from mindmap_generator import generate_mindmap, generate_simple_mindmap, MindMapRequest

app = FastAPI(
    title="Research Inbox API",
    description="LangGraph multi-agent system for research inbox cards",
    version="1.0.0"
)

# Add CORS middleware - must be added before routes
# For development, allow all localhost origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


class InboxRequest(BaseModel):
    """Request model for inbox search."""
    user_query: str = Field(..., description="User's search query")
    intent: Optional[str] = Field(None, description="Intent: grants, papers, news, or all (default)")
    lab_url: Optional[str] = Field(None, description="Optional lab URL")
    lab_profile: Optional[dict] = Field(None, description="Optional lab profile data")


class UrlResearchRequest(BaseModel):
    """Request model for URL-based research."""
    url: str = Field(..., description="Research lab URL to analyze")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Research Inbox API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/inbox", response_model=dict)
async def get_inbox(request: InboxRequest):
    """
    Get ranked inbox cards based on user query and intent.
    
    - **user_query**: Search query (required)
    - **intent**: One of "grants", "papers", "news", or "all" (optional, defaults to "all")
    - **lab_url**: Optional lab URL
    - **lab_profile**: Optional lab profile data
    """
    try:
        # Create state from request
        state = ResearchState(
            user_query=request.user_query,
            intent=request.intent,
            lab_url=request.lab_url,
            lab_profile=request.lab_profile,
        )
        
        # Invoke orchestrator
        result = ORCHESTRATOR.invoke(state)
        
        # Convert result to dict (LangGraph returns dict)
        if isinstance(result, dict):
            return result
        else:
            return result.model_dump()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/api/inbox", response_model=dict)
async def get_inbox_get(user_query: str, intent: Optional[str] = None):
    """
    GET endpoint for inbox search (alternative to POST).
    
    - **user_query**: Search query (required query parameter)
    - **intent**: One of "grants", "papers", "news", or "all" (optional query parameter)
    """
    try:
        state = ResearchState(
            user_query=user_query,
            intent=intent,
        )
        
        result = ORCHESTRATOR.invoke(state)
        
        if isinstance(result, dict):
            return result
        else:
            return result.model_dump()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/api/url-research", response_model=dict)
async def get_url_research(request: UrlResearchRequest):
    """
    Get research results (grants, papers, news) based on a research lab URL.
    
    This endpoint:
    1. Web scrapes the provided URL
    2. Extracts research-relevant keywords using LLM
    3. Queries grants.gov, PubMed, and NewsAPI with those keywords
    4. Caches results in MongoDB for future requests
    5. Returns ranked results matching the inbox format
    
    - **url**: Research lab URL to analyze (required)
    
    If the URL has been requested before, cached results are returned immediately.
    """
    if not URL_RESEARCH_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail=f"URL research service unavailable: {URL_RESEARCH_ERROR}"
        )
    
    try:
        # Validate URL format
        url = request.url.strip()
        if not url:
            raise HTTPException(status_code=400, detail="URL cannot be empty")
        
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        # Process URL research
        result = process_url_research(url)
        
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URL research: {str(e)}")


@app.get("/api/mongodb-status", response_model=dict)
async def get_mongodb_status_endpoint():
    """
    Get MongoDB connection status and diagnostics.
    
    Useful for debugging MongoDB connection issues.
    Returns detailed error information if MongoDB is not connected.
    """
    if not MONGODB_STATUS_AVAILABLE:
        return {
            "connected": False,
            "mongodb_uri_set": False,
            "database_name": None,
            "message": "MongoDB module not available"
        }
    
    try:
        status = get_mongodb_status()
        
        response = {
            "connected": status["connected"],
            "mongodb_uri_set": status["mongodb_uri_set"],
            "database_name": status["db_name"],
        }
        
        if not status["connected"]:
            response["error"] = {
                "type": status["last_error"],
                "details": status["error_details"],
                "diagnostics": status.get("diagnostics", {})
            }
            response["message"] = "MongoDB caching is DISABLED. Results will not be persisted."
        else:
            response["message"] = "MongoDB is connected and ready for caching."
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking MongoDB status: {str(e)}")


@app.post("/api/mindmap", response_model=dict)
async def generate_mindmap_endpoint(request: MindMapRequest):
    """
    Generate a mind map from research results using OpenAI.
    
    This endpoint:
    1. Takes grants, papers, and news results
    2. Uses OpenAI to identify themes and connections
    3. Returns markdown formatted for markmap.js visualization
    
    Request body should contain:
    - **grants**: List of grant cards
    - **papers**: List of paper cards  
    - **news**: List of news cards
    - **user_query**: Original search query (optional, for context)
    
    Returns:
    - **markdown**: Hierarchical markdown for markmap.js
    - **themes**: List of identified themes
    - **connections**: Cross-type connections found
    """
    try:
        # Convert Pydantic models to dicts
        grants = [g if isinstance(g, dict) else g for g in request.grants]
        papers = [p if isinstance(p, dict) else p for p in request.papers]
        news = [n if isinstance(n, dict) else n for n in request.news]
        
        # Check if we have any data
        if not grants and not papers and not news:
            return {
                "markdown": "# No Data\n\n## No research results provided",
                "themes": [],
                "connections": []
            }
        
        # Generate mindmap using OpenAI
        result = generate_mindmap(
            grants=grants,
            papers=papers,
            news=news,
            user_query=request.user_query
        )
        
        return {
            "markdown": result.markdown,
            "themes": result.themes,
            "connections": result.connections
        }
        
    except Exception as e:
        # Fallback to simple mindmap if OpenAI fails
        try:
            simple_md = generate_simple_mindmap(
                grants=request.grants,
                papers=request.papers,
                news=request.news,
                user_query=request.user_query
            )
            return {
                "markdown": simple_md,
                "themes": [],
                "connections": [],
                "error": f"OpenAI analysis failed, using simple structure: {str(e)}"
            }
        except Exception as e2:
            raise HTTPException(
                status_code=500, 
                detail=f"Error generating mind map: {str(e2)}"
            )


@app.post("/api/mindmap/simple", response_model=dict)
async def generate_simple_mindmap_endpoint(request: MindMapRequest):
    """
    Generate a simple hierarchical mind map without OpenAI analysis.
    
    Faster alternative that creates a basic structure grouping
    items by type (grants, papers, news) without theme analysis.
    """
    try:
        markdown = generate_simple_mindmap(
            grants=request.grants,
            papers=request.papers,
            news=request.news,
            user_query=request.user_query
        )
        
        return {
            "markdown": markdown,
            "themes": ["Grants", "Papers", "News"],
            "connections": []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating simple mind map: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
