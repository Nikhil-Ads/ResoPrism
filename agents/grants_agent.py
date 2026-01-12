"""Grants agent subgraph that fetches grant opportunities."""

import httpx
from datetime import datetime
from langgraph.graph import StateGraph, END
from models import ResearchState, GrantCard
from research_retriever import ResearchRetriever

# Grants.gov API endpoint
GRANTS_API_URL = "https://api.grants.gov/v1/api/search2"


def _calculate_score(opp: dict, query: str) -> float:
    """Calculate relevance score based on query match and opportunity attributes."""
    score = 0.5  # Base score
    
    title = (opp.get("title") or "").lower()
    query_lower = query.lower()
    
    # Boost for title match
    query_words = query_lower.split()
    matches = sum(1 for word in query_words if word in title)
    score += min(0.4, matches * 0.15)
    
    # Boost for open opportunities
    if opp.get("oppStatus") == "posted":
        score += 0.1
    
    return min(score, 1.0)


def _determine_badge_from_date(close_date_str: str) -> str | None:
    """Determine badge based on close date string (supports MM/DD/YYYY format)."""
    if close_date_str:
        try:
            # closeDate format: MM/DD/YYYY
            close_date = datetime.strptime(close_date_str, "%m/%d/%Y")
            days_until_close = (close_date - datetime.now()).days
            if 0 <= days_until_close <= 30:
                return "Closing soon"
            elif days_until_close < 0:
                return "Closed"
        except ValueError:
            pass
    return None


def _determine_badge(opp: dict) -> str | None:
    """Determine badge based on opportunity attributes."""
    close_date_str = opp.get("closeDate")
    if close_date_str:
        badge = _determine_badge_from_date(close_date_str)
        if badge:
            return badge
    
    # Badge for forecasted opportunities
    if opp.get("oppStatus") == "forecasted":
        return "Forecasted"
    
    return None


def fetch_grants_from_api(query: str, rows: int = 10) -> list[dict]:
    """Fetch grants from grants.gov search2 API."""
    payload = {
        "keyword": query,
        "rows": rows,
        "oppStatuses": "posted",
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(GRANTS_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


def grants_node(state: ResearchState) -> ResearchState:
    """
    Node that fetches grant opportunities from MongoDB vector search first,
    then falls back to grants.gov API if no results are found.
    """
    try:
        user_query = state.user_query
        grants = []
        
        # Try MongoDB vector search first
        print(f"[Grants Agent] Attempting MongoDB vector search for query: '{user_query}'")
        try:
            retriever = ResearchRetriever()
            mongo_results = retriever.search_grants(user_query, limit=10)
            
            if mongo_results:
                print(f"[Grants Agent] [OK] MongoDB returned {len(mongo_results)} results - using MongoDB data")
                # Transform MongoDB results to GrantCard objects
                for item in mongo_results:
                    title = item.get("title") or "Untitled Opportunity"
                    score = item.get("score", 0.5)  # Use vectorSearchScore
                    meta = item.get("meta", {})
                    
                    # Extract fields from meta dict
                    close_date = meta.get("close_date")
                    sponsor = meta.get("sponsor") or meta.get("agency_name")
                    amount_max = meta.get("amount_max")
                    opp_number = meta.get("opp_number")
                    opp_status = meta.get("opp_status")
                    post_date = meta.get("post_date")
                    badge = meta.get("badge")
                    
                    # If badge not in meta, determine it from close_date
                    if not badge and close_date:
                        badge = _determine_badge_from_date(close_date)
                    
                    # Create grant card with base fields
                    grant_card = GrantCard.create(
                        title=title,
                        score=min(1.0, max(0.0, score)),  # Ensure score is between 0 and 1
                        close_date=close_date,
                        amount_max=amount_max,
                        sponsor=sponsor,
                        badge=badge,
                        source="mongodb",
                    )
                    
                    # Add additional fields to meta
                    if opp_number:
                        grant_card.meta["opp_number"] = opp_number
                    if opp_status:
                        grant_card.meta["opp_status"] = opp_status
                    if post_date:
                        grant_card.meta["post_date"] = post_date
                    if meta.get("agency_code"):
                        grant_card.meta["agency_code"] = meta.get("agency_code")
                    
                    grants.append(grant_card)
                print(f"[Grants Agent] [OK] Successfully created {len(grants)} grant cards from MongoDB")
        except Exception as mongo_error:
            # If MongoDB search fails, fall through to API fallback
            print(f"[Grants Agent] [X] MongoDB search failed: {str(mongo_error)}")
            print(f"[Grants Agent] -> Falling back to grants.gov API")
        
        # Fall back to API if no results from MongoDB
        if not grants:
            print(f"[Grants Agent] [X] MongoDB returned 0 results")
            print(f"[Grants Agent] -> Falling back to grants.gov API")
            # Fetch from grants.gov API
            print(f"[Grants Agent] Fetching from grants.gov API...")
            api_response = fetch_grants_from_api(user_query, rows=10)
            
            # Parse opportunities from response (nested under 'data')
            data = api_response.get("data", {})
            opportunities = data.get("oppHits", [])
            
            for opp in opportunities:
                # Extract fields from API response
                title = opp.get("title") or "Untitled Opportunity"
                close_date = opp.get("closeDate")  # Format: MM/DD/YYYY
                agency_name = opp.get("agency") or opp.get("agencyCode")
                opp_number = opp.get("oppNumber")
                opp_status = opp.get("oppStatus")
                post_date = opp.get("postDate")
                
                # Calculate relevance score
                score = _calculate_score(opp, user_query)
                
                # Determine badge
                badge = _determine_badge(opp)
                
                # Create grant card with base fields
                grant_card = GrantCard.create(
                    title=title,
                    score=score,
                    close_date=close_date,
                    amount_max=None,  # Not available in search results
                    sponsor=agency_name,
                    badge=badge,
                    source="grants.gov",
                )
                
                # Add additional fields to meta
                if opp_number:
                    grant_card.meta["opp_number"] = opp_number
                if opp_status:
                    grant_card.meta["opp_status"] = opp_status
                if post_date:
                    grant_card.meta["post_date"] = post_date
                if opp.get("agencyCode"):
                    grant_card.meta["agency_code"] = opp.get("agencyCode")
                
                grants.append(grant_card)
            
            print(f"[Grants Agent] [OK] Successfully fetched {len(grants)} grants from grants.gov API")
        
        # Sort by score descending
        grants.sort(key=lambda g: g.score, reverse=True)
        
        state_dict = state.model_dump()
        state_dict["grants"] = grants
        return ResearchState(**state_dict)
    
    except Exception as e:
        # On error, append to errors list and return empty grants
        errors = state.errors + [f"GrantsAgentGraph error: {str(e)}"]
        state_dict = state.model_dump()
        state_dict["grants"] = []
        state_dict["errors"] = errors
        return ResearchState(**state_dict)


# Build the grants agent graph
grants_workflow = StateGraph(ResearchState)
grants_workflow.add_node("fetch_grants", grants_node)
grants_workflow.set_entry_point("fetch_grants")
grants_workflow.add_edge("fetch_grants", END)

GrantsAgentGraph = grants_workflow.compile()
