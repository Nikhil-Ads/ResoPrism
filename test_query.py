"""Test the orchestrator workflow with a specific query."""

import sys
import io
from orchestrator import ORCHESTRATOR
from models import ResearchState

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def print_paper_card(paper, index):
    """Print a paper card in a readable format."""
    print(f"\n[{index}] {paper.title}")
    print(f"    Score: {paper.score:.2f}")
    if paper.badge:
        print(f"    Badge: {paper.badge}")
    if paper.meta.get("published_date"):
        print(f"    Published: {paper.meta['published_date']}")
    if paper.meta.get("authors"):
        authors = paper.meta["authors"]
        if len(authors) > 0:
            print(f"    Authors: {', '.join(authors[:3])}", end="")
            if len(authors) > 3:
                print(f" and {len(authors) - 3} more")
            else:
                print()
    print(f"    Source: {paper.meta.get('source', 'N/A')}")


def test_query(query: str, intent: str = "all"):
    """Test orchestrator with a specific query."""
    print("=" * 80)
    print(f"Testing Orchestrator Workflow")
    print("=" * 80)
    print(f"\nQuery: '{query}'")
    print(f"Intent: '{intent}'")
    print("=" * 80)
    
    state = ResearchState(
        user_query=query,
        intent=intent
    )
    
    result = ORCHESTRATOR.invoke(state)
    
    if isinstance(result, dict):
        result = ResearchState(**result)
    
    print(f"\nResults Summary:")
    print(f"  Papers: {len(result.papers)}")
    print(f"  Grants: {len(result.grants)}")
    print(f"  News: {len(result.news)}")
    print(f"  Total inbox cards: {len(result.inbox_cards)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.papers:
        print(f"\n{'='*80}")
        print(f"Papers ({len(result.papers)}):")
        print("-" * 80)
        for i, paper in enumerate(result.papers, 1):
            print_paper_card(paper, i)
    
    if result.inbox_cards:
        print(f"\n{'='*80}")
        print(f"Top 10 Ranked Inbox Cards:")
        print("-" * 80)
        for i, card in enumerate(result.inbox_cards[:10], 1):
            print(f"\n[{i}] [{card.type.upper()}] {card.title}")
            print(f"    Score: {card.score:.2f}")
            if card.badge:
                print(f"    Badge: {card.badge}")
            if card.type == "paper" and card.meta.get("published_date"):
                print(f"    Published: {card.meta['published_date']}")
    
    print(f"\n{'='*80}")
    print("Test Complete!")
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    query = "environment"
    print(f"\nTesting Orchestrator with query: '{query}'")
    print("Note: This will make real API calls to NCBI with rate limiting (< 3 req/sec)\n")
    
    try:
        result = test_query(query, intent="all")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
