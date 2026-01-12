"""
FastAPI server for Research Inbox Orchestrator
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
from models import ResearchState, InboxCard, GrantCard, PaperCard, NewsCard
from orchestrator import ORCHESTRATOR
from ai_summarizer import generate_sector_summary
from mind_map.mindmap_generator import generate_mindmap, generate_simple_mindmap, MindMapResponse

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
    text_chunks: Optional[list[str]] = Field(None, description="Optional list of text chunks for keyword extraction")


class SearchResponse(BaseModel):
    """Response model for orchestrator search."""
    user_query: str = Field(..., description="Original search query")
    intent: Optional[str] = Field(None, description="Intent used for search")
    extracted_keywords: Optional[list[str]] = Field(None, description="Top keywords extracted from chunks (if chunks were provided)")
    grants: list[dict] = Field(..., description="List of grant cards")
    papers: list[dict] = Field(..., description="List of paper cards")
    news: list[dict] = Field(..., description="List of news cards")
    inbox_cards: list[dict] = Field(..., description="Merged and ranked inbox cards")
    errors: list[str] = Field(..., description="List of error messages")
    summary: dict = Field(..., description="Summary statistics")


class SummaryRequest(BaseModel):
    """Request model for AI summary generation."""
    results: list[dict] = Field(..., description="List of cards (grants, papers, or news) for the sector")
    sector: Literal["grants", "papers", "news"] = Field(..., description="Sector type: grants, papers, or news")
    lab_profile: Optional[dict] = Field(None, description="Optional lab profile information")


class SummaryResponse(BaseModel):
    """Response model for AI summary generation."""
    summary: str = Field(..., description="AI-generated summary text")
    sector: str = Field(..., description="Sector type that was summarized")


class MindMapRequest(BaseModel):
    """Request model for mind map generation."""
    grants: list[dict] = Field(default_factory=list, description="List of grant cards")
    papers: list[dict] = Field(default_factory=list, description="List of paper cards")
    news: list[dict] = Field(default_factory=list, description="List of news cards")
    user_query: Optional[str] = Field(None, description="Original search query for context")
    use_ai: bool = Field(True, description="Use AI to find themes (True) or simple hierarchy (False)")


class MindMapApiResponse(BaseModel):
    """Response model for mind map generation."""
    markdown: str = Field(..., description="Markdown content for markmap.js")
    themes: list[str] = Field(default_factory=list, description="Identified themes")
    connections: list[dict] = Field(default_factory=list, description="Cross-type connections found")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Research Inbox Orchestrator API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "search": "/api/search (POST)",
            "generate_summary": "/api/generate-summary (POST)",
            "generate_mindmap": "/api/generate-mindmap (POST)",
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
            lab_profile=request.lab_profile,
            text_chunks=request.text_chunks
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
            extracted_keywords=result_state.extracted_keywords,
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


@app.post("/api/generate-summary", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest):
    """
    Generate AI-powered summary for a specific sector (grants, papers, or news).
    
    Args:
        request: SummaryRequest with results array, sector type, and optional lab_profile
        
    Returns:
        SummaryResponse with AI-generated summary text
    """
    try:
        # Convert dict results back to appropriate card types using Pydantic model_validate
        cards = []
        if request.sector == "grants":
            for item in request.results:
                cards.append(GrantCard.model_validate(item))
        elif request.sector == "papers":
            for item in request.results:
                cards.append(PaperCard.model_validate(item))
        elif request.sector == "news":
            for item in request.results:
                cards.append(NewsCard.model_validate(item))
        
        # Generate summary using AI summarizer with lab profile
        summary_text = generate_sector_summary(cards, request.sector, request.lab_profile)
        
        return SummaryResponse(
            summary=summary_text,
            sector=request.sector
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation error: {str(e)}")


@app.post("/api/generate-mindmap", response_model=MindMapApiResponse)
async def generate_mindmap_endpoint(request: MindMapRequest):
    """
    Generate a mind map visualization from research results.
    
    Args:
        request: MindMapRequest with grants, papers, news arrays and optional user_query
        
    Returns:
        MindMapApiResponse with markdown for markmap.js, themes, and connections
    """
    try:
        if request.use_ai:
            # Use AI-powered thematic analysis
            result = generate_mindmap(
                grants=request.grants,
                papers=request.papers,
                news=request.news,
                user_query=request.user_query
            )
            return MindMapApiResponse(
                markdown=result.markdown,
                themes=result.themes,
                connections=result.connections
            )
        else:
            # Use simple hierarchical structure
            markdown = generate_simple_mindmap(
                grants=request.grants,
                papers=request.papers,
                news=request.news,
                user_query=request.user_query
            )
            return MindMapApiResponse(
                markdown=markdown,
                themes=[],
                connections=[]
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mind map generation error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
