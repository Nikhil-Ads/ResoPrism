"""Pydantic models for research inbox state and card schemas."""

import hashlib
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class InboxCard(BaseModel):
    """Base card schema for all inbox card types."""
    
    id: str = Field(..., description="Deterministic ID based on content")
    type: Literal["grant", "paper", "news"]
    title: str
    score: float = Field(..., ge=0.0, le=1.0, description="Score between 0 and 1")
    badge: Optional[str] = None
    meta: dict = Field(default_factory=dict)
    embedding: Optional[list[float]] = Field(default=None, description="Vector embedding for semantic search")


class GrantCard(InboxCard):
    """Grant-specific card schema."""
    
    type: Literal["grant"] = "grant"
    meta: dict = Field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        title: str,
        score: float,
        close_date: Optional[str] = None,
        amount_max: Optional[float] = None,
        sponsor: Optional[str] = None,
        badge: Optional[str] = None,
        source: str = "grants.gov",
    ) -> "GrantCard":
        """Create a GrantCard with deterministic ID generation."""
        meta = {
            "close_date": close_date,
            "amount_max": amount_max,
            "sponsor": sponsor,
            "source": source,
        }
        # Generate deterministic ID from type, title, and key meta fields
        id_str = f"grant|{title}|{close_date or ''}|{sponsor or ''}"
        card_id = hashlib.sha256(id_str.encode()).hexdigest()[:16]
        
        return cls(
            id=card_id,
            type="grant",
            title=title,
            score=score,
            badge=badge,
            meta={k: v for k, v in meta.items() if v is not None},
        )


class PaperCard(InboxCard):
    """Paper-specific card schema."""
    
    type: Literal["paper"] = "paper"
    meta: dict = Field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        title: str,
        score: float,
        published_date: Optional[str] = None,
        authors: Optional[list[str]] = None,
        badge: Optional[str] = None,
        source: str = "pubmed",
    ) -> "PaperCard":
        """Create a PaperCard with deterministic ID generation."""
        meta = {
            "published_date": published_date,
            "authors": authors or [],
            "source": source,
        }
        # Generate deterministic ID from type, title, and key meta fields
        authors_str = ",".join(authors) if authors else ""
        id_str = f"paper|{title}|{published_date or ''}|{authors_str}"
        card_id = hashlib.sha256(id_str.encode()).hexdigest()[:16]
        
        return cls(
            id=card_id,
            type="paper",
            title=title,
            score=score,
            badge=badge,
            meta={k: v for k, v in meta.items() if v is not None},
        )


class NewsCard(InboxCard):
    """News-specific card schema."""
    
    type: Literal["news"] = "news"
    meta: dict = Field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        title: str,
        score: float,
        published_date: Optional[str] = None,
        outlet: Optional[str] = None,
        url: Optional[str] = None,
        badge: Optional[str] = None,
        source: str = "newsapi",
    ) -> "NewsCard":
        """Create a NewsCard with deterministic ID generation."""
        meta = {
            "published_date": published_date,
            "outlet": outlet,
            "url": url,
            "source": source,
        }
        # Generate deterministic ID from type, title, and key meta fields
        id_str = f"news|{title}|{published_date or ''}|{outlet or ''}"
        card_id = hashlib.sha256(id_str.encode()).hexdigest()[:16]
        
        return cls(
            id=card_id,
            type="news",
            title=title,
            score=score,
            badge=badge,
            meta={k: v for k, v in meta.items() if v is not None},
        )


class ResearchState(BaseModel):
    """Shared state contract for orchestrator and subagents."""
    
    # Input fields
    user_query: str = Field(..., description="User's search query")
    intent: Optional[str] = Field(None, description="Intent: grants, papers, news, or all")
    lab_url: Optional[str] = Field(None, description="Optional lab URL")
    lab_profile: Optional[dict] = Field(None, description="Optional lab profile data")
    text_chunks: Optional[list[str]] = Field(None, description="Optional list of text chunks for keyword extraction")
    extracted_keywords: Optional[list[str]] = Field(None, description="Top keywords extracted from chunks")
    
    # Output fields (default to empty lists)
    grants: list[GrantCard] = Field(default_factory=list, description="Grant cards from GrantsAgentGraph")
    papers: list[PaperCard] = Field(default_factory=list, description="Paper cards from PapersAgentGraph")
    news: list[NewsCard] = Field(default_factory=list, description="News cards from NewsAgentGraph")
    inbox_cards: list[InboxCard] = Field(default_factory=list, description="Merged and ranked inbox cards")
    
    # Error tracking
    errors: list[str] = Field(default_factory=list, description="List of error messages")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
