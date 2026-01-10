"""Papers agent subgraph that fetches research papers."""

from langgraph.graph import StateGraph, END
from models import ResearchState, PaperCard


def papers_node(state: ResearchState) -> ResearchState:
    """
    Node that fetches research papers.
    For MVP, returns stub data. Later can be replaced with NCBI E-utilities API calls.
    """
    try:
        user_query = state.user_query
        # lab_profile = state.lab_profile  # Can be used for filtering later
        
        # Stub data - return 2-3 sample papers matching the schema
        papers = [
            PaperCard.create(
                title="Machine Learning Applications in Healthcare: A Comprehensive Review",
                score=0.82,
                published_date="2024-01-15",
                authors=["Smith, J.", "Doe, A.", "Johnson, B."],
                badge="High impact",
                source="pubmed",
            ),
            PaperCard.create(
                title="Deep Learning for Medical Image Analysis: Recent Advances",
                score=0.75,
                published_date="2024-02-20",
                authors=["Chen, L.", "Wang, M.", "Zhang, K."],
                source="pubmed",
            ),
            PaperCard.create(
                title="Predictive Modeling in Clinical Decision Support Systems",
                score=0.68,
                published_date="2024-03-10",
                authors=["Brown, R.", "Davis, S."],
                source="pubmed",
            ),
        ]
        
        # Filter based on user_query if needed (simple stub logic)
        # For now, return all papers
        
        state_dict = state.model_dump()
        state_dict["papers"] = papers
        return ResearchState(**state_dict)
    
    except Exception as e:
        # On error, append to errors list and return empty papers
        errors = state.errors + [f"PapersAgentGraph error: {str(e)}"]
        state_dict = state.model_dump()
        state_dict["papers"] = []
        state_dict["errors"] = errors
        return ResearchState(**state_dict)


# Build the papers agent graph
papers_workflow = StateGraph(ResearchState)
papers_workflow.add_node("papers", papers_node)
papers_workflow.set_entry_point("papers")
papers_workflow.add_edge("papers", END)

PapersAgentGraph = papers_workflow.compile()
