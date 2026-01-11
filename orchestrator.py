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

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from models import ResearchState, InboxCard, GrantCard, PaperCard, NewsCard
from agents import GrantsAgentGraph, PapersAgentGraph, NewsAgentGraph
from ranking import rank_cards
from keyword_extraction import extract_top_keywords

# Load environment variables once at the orchestrator level
load_dotenv()

# Valid intents
VALID_INTENTS = {"grants", "papers", "news", "all"}


def validate_input(state: ResearchState) -> ResearchState:
    """
    Normalize intent (missing/unknown -> "all"), validate user_query.
    If text_chunks are provided, extract keywords from them.
    """
    intent = state.intent
    if not intent or intent not in VALID_INTENTS:
        intent = "all"
    
    # Validate user_query is not empty (unless text_chunks are provided)
    if not state.text_chunks and (not state.user_query or not state.user_query.strip()):
        errors = state.errors + ["user_query cannot be empty if text_chunks are not provided"]
        state_dict = state.model_dump()
        state_dict["intent"] = "all"
        state_dict["errors"] = errors
        return ResearchState(**state_dict)
    
    state_dict = state.model_dump()
    state_dict["intent"] = intent
    
    # If text_chunks are provided, extract keywords
    if state.text_chunks and len(state.text_chunks) > 0:
        try:
            # Extract top 5 keywords from chunks
            keywords = extract_top_keywords(state.text_chunks, top_k=5, use_llm=True)
            state_dict["extracted_keywords"] = keywords
            # If no user_query is provided but keywords are extracted, use first keyword as default
            if not state.user_query or not state.user_query.strip():
                state_dict["user_query"] = keywords[0] if keywords else ""
        except Exception as e:
            errors = state.errors + [f"Keyword extraction failed: {str(e)}"]
            state_dict["errors"] = errors
    
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
    If extracted_keywords exist, calls the agent once per keyword and aggregates results.
    """
    # Check if we have extracted keywords
    keywords = state.extracted_keywords
    if keywords and len(keywords) > 0:
        # Call agent multiple times (once per keyword)
        all_results = []
        accumulated_errors = state.errors.copy()
        
        for keyword in keywords:
            try:
                # Create a new state with the keyword as user_query
                # Don't pass existing results for the current agent type to avoid accumulation
                # Instead, we collect fresh results for each keyword and aggregate at the end
                keyword_state_dict = {
                    "user_query": keyword,
                    "intent": state.intent,
                    "lab_url": state.lab_url,
                    "lab_profile": state.lab_profile,
                    "text_chunks": None,  # Don't pass chunks again
                    "extracted_keywords": None,  # Don't pass keywords to avoid recursion
                    "grants": [],
                    "papers": [],
                    "news": [],
                    "inbox_cards": [],
                    "errors": []
                }
                # Preserve results from other agents (for all_node scenario)
                if agent_name != "GrantsAgentGraph":
                    keyword_state_dict["grants"] = state.grants.copy()
                if agent_name != "PapersAgentGraph":
                    keyword_state_dict["papers"] = state.papers.copy()
                if agent_name != "NewsAgentGraph":
                    keyword_state_dict["news"] = state.news.copy()
                
                keyword_state = ResearchState(**keyword_state_dict)
                
                result = graph.invoke(keyword_state)
                # Convert dict result back to ResearchState if needed
                if isinstance(result, dict):
                    result_state = ResearchState(**result)
                else:
                    result_state = result
                
                # Collect results based on agent type
                if agent_name == "GrantsAgentGraph":
                    all_results.extend(result_state.grants)
                elif agent_name == "PapersAgentGraph":
                    all_results.extend(result_state.papers)
                elif agent_name == "NewsAgentGraph":
                    all_results.extend(result_state.news)
                
                # Collect errors
                accumulated_errors.extend(result_state.errors)
                
            except Exception as e:
                accumulated_errors.append(f"{agent_name} error for keyword '{keyword}': {str(e)}")
                continue
        
        # Deduplicate results by ID
        seen_ids = set()
        unique_results = []
        for item in all_results:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_results.append(item)
        
        # Update state with aggregated results, preserving existing results from other agents
        state_dict = state.model_dump()
        if agent_name == "GrantsAgentGraph":
            state_dict["grants"] = unique_results
        elif agent_name == "PapersAgentGraph":
            state_dict["papers"] = unique_results
        elif agent_name == "NewsAgentGraph":
            state_dict["news"] = unique_results
        state_dict["errors"] = accumulated_errors
        # Preserve other fields that might have been set
        return ResearchState(**state_dict)
    else:
        # Normal single query invocation
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
