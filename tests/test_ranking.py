"""Unit tests for ranking logic."""

import pytest
from ranking import rank_cards
from models import GrantCard, PaperCard, NewsCard
from tests.fixtures import get_tiebreak_test_cards


def test_rank_by_score_descending():
    """Test that cards are ranked by score in descending order."""
    cards = [
        GrantCard.create(title="Low Score", score=0.5, sponsor="Test"),
        PaperCard.create(title="High Score", score=0.9, authors=["A"]),
        NewsCard.create(title="Medium Score", score=0.7, outlet="Test"),
    ]
    
    ranked = rank_cards(cards)
    
    assert len(ranked) == 3
    assert ranked[0].score == 0.9
    assert ranked[1].score == 0.7
    assert ranked[2].score == 0.5


def test_rank_type_priority_tiebreaker():
    """Test that type priority (grant > paper > news) breaks ties."""
    cards = get_tiebreak_test_cards()
    
    ranked = rank_cards(cards)
    
    assert len(ranked) == 3
    # All have score 0.75, so should be sorted by type priority
    assert ranked[0].type == "grant"  # Highest priority
    assert ranked[1].type == "paper"
    assert ranked[2].type == "news"   # Lowest priority


def test_rank_title_alphabetical_tiebreaker():
    """Test that title alphabetical order breaks ties for same score and type."""
    cards = [
        GrantCard.create(title="Zebra Grant", score=0.75, sponsor="Test"),
        GrantCard.create(title="Alpha Grant", score=0.75, sponsor="Test"),
        GrantCard.create(title="Beta Grant", score=0.75, sponsor="Test"),
    ]
    
    ranked = rank_cards(cards)
    
    assert len(ranked) == 3
    assert ranked[0].title == "Alpha Grant"
    assert ranked[1].title == "Beta Grant"
    assert ranked[2].title == "Zebra Grant"


def test_rank_complex_mixed_scoring():
    """Test ranking with mixed scores, types, and titles."""
    cards = [
        PaperCard.create(title="B Paper", score=0.8, authors=["A"]),
        GrantCard.create(title="A Grant", score=0.8, sponsor="Test"),
        NewsCard.create(title="C News", score=0.8, outlet="Test"),
        PaperCard.create(title="D Paper", score=0.9, authors=["A"]),
    ]
    
    ranked = rank_cards(cards)
    
    assert len(ranked) == 4
    # Highest score first
    assert ranked[0].score == 0.9
    assert ranked[0].title == "D Paper"
    # Then 0.8 scores sorted by type priority (grant > paper > news)
    assert ranked[1].type == "grant"
    assert ranked[1].title == "A Grant"
    assert ranked[2].type == "paper"
    assert ranked[2].title == "B Paper"
    assert ranked[3].type == "news"
    assert ranked[3].title == "C News"


def test_rank_empty_list():
    """Test that ranking empty list returns empty list."""
    ranked = rank_cards([])
    assert ranked == []
