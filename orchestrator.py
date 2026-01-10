"""
Research Inbox Orchestrator

State Contract:
- Input: user_query (required), intent (optional), lab_url, lab_profile
- Output: grants, papers, news (lists), inbox_cards (ranked list), errors

Supported Intents:
- "grants": Run only GrantsAgentGraph
- "papers": Run only PapersAgentGraph  
- "news": Run only NewsAgentGraph
- "all" (default): Run all three agents

Output Schema (inbox_cards):
- id: str (deterministic)
- type: "grant" | "paper" | "news"
- title: str
- score: float
- badge: Optional[str]
- meta: dict (type-specific fields)

Run Tests:
    pytest tests/
"""

from langgraph.graph import StateGraph, END
from models import ResearchState, InboxCard, GrantCard, PaperCard, NewsCard
from agents import GrantsAgentGraph, PapersAgentGraph, NewsAgentGraph
from ranking import rank_cards

# Valid intents
VALID_INTENTS = {"grants", "papers", "news", "all"}


def validate_input(state: ResearchState) -> ResearchState:
    """
    Normalize intent (missing/unknown -> "all"), validate user_query.
    """
    intent = state.intent
    if not intent or intent not in VALID_INTENTS:
        intent = "all"
    
    # Validate user_query is not empty
    if not state.user_query or not state.user_query.strip():
        errors = state.errors + ["user_query cannot be empty"]
        state_dict = state.model_dump()
        state_dict["intent"] = "all"
        state_dict["errors"] = errors
        return ResearchState(**state_dict)
    
    state_dict = state.model_dump()
    state_dict["intent"] = intent
    return ResearchState(**state_dict)


def route_intent(state: ResearchState) -> str:
    """
    Route to the appropriate node based on intent.
    Returns the node name to go to.
    """
    intent = state.intent or "all"
    return {
        "grants": "grants_node",
        "papers": "papers_node",
        "news": "news_node",
        "all": "all_node",
    }.get(intent, "all_node")


def invoke_subagent(graph, state: ResearchState, agent_name: str) -> ResearchState:
    """
    Helper that wraps subagent.invoke() with error handling.
    """
    try:
        result = graph.invoke(state)
        # Convert dict result back to ResearchState
        if isinstance(result, dict):
            return ResearchState(**result)
        return result
    except Exception as e:
        errors = state.errors + [f"{agent_name} error: {str(e)}"]
        # Return state with updated errors
        state_dict = state.model_dump()
        state_dict["errors"] = errors
        return ResearchState(**state_dict)


def grants_node(state: ResearchState) -> ResearchState:
    """Invoke grants agent only."""
    return invoke_subagent(GrantsAgentGraph, state, "GrantsAgentGraph")


def papers_node(state: ResearchState) -> ResearchState:
    """Invoke papers agent only."""
    return invoke_subagent(PapersAgentGraph, state, "PapersAgentGraph")


def news_node(state: ResearchState) -> ResearchState:
    """Invoke news agent only."""
    return invoke_subagent(NewsAgentGraph, state, "NewsAgentGraph")


def all_node(state: ResearchState) -> ResearchState:
    """
    Invoke all three agents sequentially.
    Each agent writes to its own key and doesn't overwrite others.
    """
    # Start with current state
    current_state = state
    
    # Invoke each agent sequentially
    current_state = invoke_subagent(GrantsAgentGraph, current_state, "GrantsAgentGraph")
    current_state = invoke_subagent(PapersAgentGraph, current_state, "PapersAgentGraph")
    current_state = invoke_subagent(NewsAgentGraph, current_state, "NewsAgentGraph")
    
    return current_state


def merge_results(state: ResearchState) -> ResearchState:
    """
    Collect grants/papers/news into unified inbox_cards list.
    """
    cards: list[InboxCard] = []
    
    # Add grants
    cards.extend(state.grants)
    
    # Add papers
    cards.extend(state.papers)
    
    # Add news
    cards.extend(state.news)
    
    state_dict = state.model_dump()
    state_dict["inbox_cards"] = cards
    return ResearchState(**state_dict)


def rank_cards_node(state: ResearchState) -> ResearchState:
    """
    Rank cards using ranking module.
    """
    ranked = rank_cards(state.inbox_cards)
    state_dict = state.model_dump()
    state_dict["inbox_cards"] = ranked
    return ResearchState(**state_dict)


# Build the orchestrator graph
orchestrator_workflow = StateGraph(ResearchState)

# Add all nodes
orchestrator_workflow.add_node("validate_input", validate_input)
orchestrator_workflow.add_node("grants_node", grants_node)
orchestrator_workflow.add_node("papers_node", papers_node)
orchestrator_workflow.add_node("news_node", news_node)
orchestrator_workflow.add_node("all_node", all_node)
orchestrator_workflow.add_node("merge_results", merge_results)
orchestrator_workflow.add_node("rank_cards", rank_cards_node)

# Set entry point
orchestrator_workflow.set_entry_point("validate_input")

# Add edges with conditional routing from validate_input
orchestrator_workflow.add_conditional_edges(
    "validate_input",
    route_intent,
    {
        "grants_node": "grants_node",
        "papers_node": "papers_node",
        "news_node": "news_node",
        "all_node": "all_node",
    }
)
orchestrator_workflow.add_edge("grants_node", "merge_results")
orchestrator_workflow.add_edge("papers_node", "merge_results")
orchestrator_workflow.add_edge("news_node", "merge_results")
orchestrator_workflow.add_edge("all_node", "merge_results")
orchestrator_workflow.add_edge("merge_results", "rank_cards")
orchestrator_workflow.add_edge("rank_cards", END)

# Compile the graph
ORCHESTRATOR = orchestrator_workflow.compile()
