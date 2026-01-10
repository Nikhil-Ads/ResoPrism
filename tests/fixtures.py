"""Test fixtures and stub data for tests."""

from models import ResearchState, GrantCard, PaperCard, NewsCard


def create_test_state(
    user_query: str,
    intent: str = None,
    lab_url: str = None,
    lab_profile: dict = None,
) -> ResearchState:
    """Helper to create test state."""
    return ResearchState(
        user_query=user_query,
        intent=intent,
        lab_url=lab_url,
        lab_profile=lab_profile,
    )


def get_stub_grant_cards() -> list[GrantCard]:
    """Return stub grant cards for testing."""
    return [
        GrantCard.create(
            title="NSF Machine Learning for Healthcare Research Grant",
            score=0.85,
            close_date="2024-12-31",
            amount_max=500000.0,
            sponsor="National Science Foundation",
            badge="Closing soon",
        ),
        GrantCard.create(
            title="NIH Biomedical AI Funding Opportunity",
            score=0.78,
            close_date="2025-03-15",
            amount_max=750000.0,
            sponsor="National Institutes of Health",
            badge="High impact",
        ),
    ]


def get_stub_paper_cards() -> list[PaperCard]:
    """Return stub paper cards for testing."""
    return [
        PaperCard.create(
            title="Machine Learning Applications in Healthcare: A Comprehensive Review",
            score=0.82,
            published_date="2024-01-15",
            authors=["Smith, J.", "Doe, A.", "Johnson, B."],
            badge="High impact",
        ),
        PaperCard.create(
            title="Deep Learning for Medical Image Analysis: Recent Advances",
            score=0.75,
            published_date="2024-02-20",
            authors=["Chen, L.", "Wang, M.", "Zhang, K."],
        ),
    ]


def get_stub_news_cards() -> list[NewsCard]:
    """Return stub news cards for testing."""
    return [
        NewsCard.create(
            title="Breakthrough in AI-Powered Medical Diagnostics Announced",
            score=0.79,
            published_date="2024-04-05",
            outlet="Science Daily",
            url="https://example.com/news1",
            badge="Breaking",
        ),
        NewsCard.create(
            title="New Healthcare Funding Initiative Targets ML Research",
            score=0.71,
            published_date="2024-04-10",
            outlet="Healthcare Tech News",
            url="https://example.com/news2",
        ),
    ]


def get_tiebreak_test_cards() -> list:
    """Return cards for testing tie-breaking logic.
    Two cards with same score (0.75), different types and titles.
    """
    return [
        PaperCard.create(
            title="Alpha Paper Title",
            score=0.75,
            published_date="2024-01-01",
            authors=["Author A"],
        ),
        GrantCard.create(
            title="Beta Grant Title",
            score=0.75,
            close_date="2025-01-01",
            sponsor="Test Sponsor",
        ),
        NewsCard.create(
            title="Gamma News Title",
            score=0.75,
            published_date="2024-01-01",
            outlet="Test Outlet",
        ),
    ]
