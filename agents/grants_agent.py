"""Grants agent subgraph that fetches grant opportunities."""

import httpx
from datetime import datetime
from langgraph.graph import StateGraph, END
from models import ResearchState, GrantCard

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


def _determine_badge(opp: dict) -> str | None:
    """Determine badge based on opportunity attributes."""
    close_date_str = opp.get("closeDate")
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
    Node that fetches grant opportunities from grants.gov API.
    """
    try:
        user_query = state.user_query
        
        # Fetch from grants.gov API
        api_response = fetch_grants_from_api(user_query, rows=10)
        
        # Parse opportunities from response (nested under 'data')
        data = api_response.get("data", {})
        opportunities = data.get("oppHits", [])
        
        grants = []
        for opp in opportunities:
            # Extract fields from API response
            title = opp.get("title") or "Untitled Opportunity"
            close_date = opp.get("closeDate")  # Format: MM/DD/YYYY
            agency_name = opp.get("agency") or opp.get("agencyCode")
            
            # Calculate relevance score
            score = _calculate_score(opp, user_query)
            
            # Determine badge
            badge = _determine_badge(opp)
            
            grants.append(
                GrantCard.create(
                    title=title,
                    score=score,
                    close_date=close_date,
                    amount_max=None,  # Not available in search results
                    sponsor=agency_name,
                    badge=badge,
                    source="grants.gov",
                )
            )
        
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
