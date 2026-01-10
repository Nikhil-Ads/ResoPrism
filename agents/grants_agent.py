"""Grants agent subgraph that fetches grant opportunities."""

from langgraph.graph import StateGraph, END
from models import ResearchState, GrantCard


def grants_node(state: ResearchState) -> ResearchState:
    """
    Node that fetches grant opportunities.
    For MVP, returns stub data. Later can be replaced with grants.gov API calls.
    """
    try:
        user_query = state.user_query
        # lab_profile = state.lab_profile  # Can be used for filtering later
        
        # Stub data - return 2-3 sample grants matching the schema
        grants = [
            GrantCard.create(
                title="NSF Machine Learning for Healthcare Research Grant",
                score=0.85,
                close_date="2024-12-31",
                amount_max=500000.0,
                sponsor="National Science Foundation",
                badge="Closing soon",
                source="grants.gov",
            ),
            GrantCard.create(
                title="NIH Biomedical AI Funding Opportunity",
                score=0.78,
                close_date="2025-03-15",
                amount_max=750000.0,
                sponsor="National Institutes of Health",
                badge="High impact",
                source="grants.gov",
            ),
            GrantCard.create(
                title="DARPA Healthcare Innovation Program",
                score=0.72,
                close_date="2025-06-30",
                amount_max=1000000.0,
                sponsor="DARPA",
                source="grants.gov",
            ),
        ]
        
        # Filter based on user_query if needed (simple stub logic)
        # For now, return all grants
        
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
grants_workflow.add_node("grants", grants_node)
grants_workflow.set_entry_point("grants")
grants_workflow.add_edge("grants", END)

GrantsAgentGraph = grants_workflow.compile()
