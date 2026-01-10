"""Ranking logic for inbox cards."""

from typing import Literal
from models import InboxCard

# Type priority order: grant > paper > news
TYPE_ORDER: dict[Literal["grant", "paper", "news"], int] = {
    "grant": 0,
    "paper": 1,
    "news": 2,
}


def rank_cards(cards: list[InboxCard]) -> list[InboxCard]:
    """
    Rank cards by score (descending), then by type priority (grant > paper > news),
    then by title (ascending, alphabetical).
    
    Args:
        cards: List of inbox cards to rank
        
    Returns:
        Sorted list of cards
    """
    if not cards:
        return []
    
    # Sort by: score (desc), type priority (asc), title (asc)
    return sorted(
        cards,
        key=lambda c: (-c.score, TYPE_ORDER[c.type], c.title)
    )
