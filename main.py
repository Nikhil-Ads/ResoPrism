"""
FastAPI server for Research Inbox Orchestrator
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
from models import ResearchState, InboxCard
from orchestrator import ORCHESTRATOR

app = FastAPI(
    title="Research Inbox Orchestrator API",
    description="Multi-agent research inbox system for grants, papers, and news",
    version="0.1.0"
)

# Enable CORS for local development and frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class SearchRequest(BaseModel):
    """Request model for orchestrator search."""
    user_query: str = Field(..., description="Search query string")
    intent: Optional[Literal["grants", "papers", "news", "all"]] = Field(
        None, 
        description="Intent: grants, papers, news, or all (default)"
    )
    lab_url: Optional[str] = Field(None, description="Optional lab URL")
    lab_profile: Optional[dict] = Field(None, description="Optional lab profile data")


class SearchResponse(BaseModel):
    """Response model for orchestrator search."""
    user_query: str = Field(..., description="Original search query")
    intent: Optional[str] = Field(None, description="Intent used for search")
    grants: list[dict] = Field(..., description="List of grant cards")
    papers: list[dict] = Field(..., description="List of paper cards")
    news: list[dict] = Field(..., description="List of news cards")
    inbox_cards: list[dict] = Field(..., description="Merged and ranked inbox cards")
    errors: list[str] = Field(..., description="List of error messages")
    summary: dict = Field(..., description="Summary statistics")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Research Inbox Orchestrator API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "search": "/api/search (POST)",
            "health": "/health (GET)",
            "docs": "/docs (GET)"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


def _card_to_dict(card: InboxCard) -> dict:
    """Convert InboxCard to dictionary for JSON serialization."""
    return {
        "id": card.id,
        "type": card.type,
        "title": card.title,
        "score": card.score,
        "badge": card.badge,
        "meta": card.meta
    }


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for grants, papers, and news based on user query.
    
    Args:
        request: SearchRequest with user_query and optional intent
        
    Returns:
        SearchResponse with grants, papers, news, and ranked inbox_cards
    """
    try:
        # Create ResearchState from request
        state = ResearchState(
            user_query=request.user_query,
            intent=request.intent,
            lab_url=request.lab_url,
            lab_profile=request.lab_profile
        )
        
        # Invoke orchestrator
        result = ORCHESTRATOR.invoke(state)
        
        # Convert result to ResearchState if needed
        if isinstance(result, dict):
            result_state = ResearchState(**result)
        else:
            result_state = result
        
        # Convert cards to dictionaries for JSON serialization
        grants = [_card_to_dict(card) for card in result_state.grants]
        papers = [_card_to_dict(card) for card in result_state.papers]
        news = [_card_to_dict(card) for card in result_state.news]
        inbox_cards = [_card_to_dict(card) for card in result_state.inbox_cards]
        
        # Create summary
        summary = {
            "total_grants": len(grants),
            "total_papers": len(papers),
            "total_news": len(news),
            "total_cards": len(inbox_cards),
            "has_errors": len(result_state.errors) > 0,
            "error_count": len(result_state.errors)
        }
        
        return SearchResponse(
            user_query=result_state.user_query,
            intent=result_state.intent or "all",
            grants=grants,
            papers=papers,
            news=news,
            inbox_cards=inbox_cards,
            errors=result_state.errors,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {str(e)}")


@app.get("/api/search")
async def search_get(query: str, intent: Optional[str] = None):
    """
    GET endpoint for search (convenience method).
    
    Args:
        query: Search query string (alias for user_query)
        intent: Optional intent (grants, papers, news, all)
        
    Returns:
        SearchResponse with results
    """
    request = SearchRequest(user_query=query, intent=intent)
    return await search(request)


@app.post("/api/inbox", response_model=SearchResponse)
async def inbox_search(request: SearchRequest):
    """
    Inbox search endpoint (alias for /api/search to match frontend).
    
    Args:
        request: SearchRequest with user_query and optional intent
        
    Returns:
        SearchResponse with grants, papers, news, and ranked inbox_cards
    """
    return await search(request)


@app.get("/api/inbox")
async def inbox_search_get(user_query: str, intent: Optional[str] = None):
    """
    GET endpoint for inbox search (alias for /api/search to match frontend).
    
    Args:
        user_query: Search query string (matches frontend parameter name)
        intent: Optional intent (grants, papers, news, all)
        
    Returns:
        SearchResponse with results
    """
    request = SearchRequest(user_query=user_query, intent=intent)
    return await search(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
