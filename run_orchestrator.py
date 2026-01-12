#!/usr/bin/env python3
"""Run the orchestrator with a test query."""

import sys
import json
from datetime import datetime
from models import ResearchState
from orchestrator import ORCHESTRATOR

def run_orchestrator(query: str, intent: str = "all"):
    """Run the orchestrator and display results."""
    print(f"\n{'='*60}")
    print(f"Research Inbox Orchestrator")
    print(f"{'='*60}")
    print(f"Query: The vast majority of human malignancies result from adenocarcinomas originating from epithelial cells")
    print(f"Intent: {intent}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Create initial state
    state = ResearchState(
        user_query=query,
        intent=intent if intent != "all" else None
    )
    
    try:
        # Invoke the orchestrator
        print("Invoking orchestrator...")
        result = ORCHESTRATOR.invoke(state)
        
        # Convert to ResearchState if needed (result is usually a dict)
        if isinstance(result, dict):
            result_state = ResearchState(**result)
        else:
            result_state = result
        
        # Display results
        print(f"\n{'='*60}")
        print("RESULTS")
        print(f"{'='*60}\n")
        
        print(f"[OK] Grants found: {len(result_state.grants)}")
        print(f"[OK] Papers found: {len(result_state.papers)}")
        print(f"[OK] News found: {len(result_state.news)}")
        print(f"[OK] Total inbox cards: {len(result_state.inbox_cards)}")
        
        if result_state.errors:
            print(f"[!] Errors: {len(result_state.errors)}")
            for error in result_state.errors:
                print(f"  - {error}")
        else:
            print(f"[OK] Errors: 0")
        
        if result_state.inbox_cards:
            print(f"\n{'='*60}")
            print(f"TOP {min(10, len(result_state.inbox_cards))} RANKED CARDS")
            print(f"{'='*60}\n")
            for i, card in enumerate(result_state.inbox_cards[:10], 1):
                print(f"{i}. [{card.type.upper()}] {card.title}")
                print(f"   Score: {card.score:.3f}")
                if card.badge:
                    print(f"   Badge: {card.badge}")
                if card.meta:
                    # Format meta nicely
                    meta_str = ", ".join([f"{k}: {v}" for k, v in card.meta.items() if v])
                    if meta_str:
                        print(f"   Meta: {meta_str}")
                print()
        else:
            print("\n[!] No inbox cards found.")
        
        print(f"{'='*60}\n")
        return result_state
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Allow query and intent from command line args
    if len(sys.argv) > 1:
        query = sys.argv[1]
        intent = sys.argv[2] if len(sys.argv) > 2 else "all"
    else:
        # Default test query
        query = "machine learning healthcare research funding"
        intent = "all"
    
    run_orchestrator(query, intent)
