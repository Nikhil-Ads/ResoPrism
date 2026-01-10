"""News agent subgraph that fetches news articles."""

from langgraph.graph import StateGraph, END
from models import ResearchState, NewsCard


def news_node(state: ResearchState) -> ResearchState:
    """
    Node that fetches news articles.
    For MVP, returns stub data. Later can be replaced with NewsAPI calls.
    """
    try:
        user_query = state.user_query
        # lab_profile = state.lab_profile  # Can be used for filtering later
        
        # Stub data - return 2-3 sample news articles matching the schema
        news = [
            NewsCard.create(
                title="Breakthrough in AI-Powered Medical Diagnostics Announced",
                score=0.79,
                published_date="2024-04-05",
                outlet="Science Daily",
                url="https://example.com/news1",
                badge="Breaking",
                source="newsapi",
            ),
            NewsCard.create(
                title="New Healthcare Funding Initiative Targets ML Research",
                score=0.71,
                published_date="2024-04-10",
                outlet="Healthcare Tech News",
                url="https://example.com/news2",
                source="newsapi",
            ),
            NewsCard.create(
                title="FDA Approves AI-Based Clinical Decision Tool",
                score=0.65,
                published_date="2024-04-15",
                outlet="Medical Innovation Journal",
                url="https://example.com/news3",
                source="newsapi",
            ),
        ]
        
        # Filter based on user_query if needed (simple stub logic)
        # For now, return all news
        
        state_dict = state.model_dump()
        state_dict["news"] = news
        return ResearchState(**state_dict)
    
    except Exception as e:
        # On error, append to errors list and return empty news
        errors = state.errors + [f"NewsAgentGraph error: {str(e)}"]
        state_dict = state.model_dump()
        state_dict["news"] = []
        state_dict["errors"] = errors
        return ResearchState(**state_dict)


# Build the news agent graph
news_workflow = StateGraph(ResearchState)
news_workflow.add_node("news", news_node)
news_workflow.set_entry_point("news")
news_workflow.add_edge("news", END)

NewsAgentGraph = news_workflow.compile()
