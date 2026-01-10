"""News agent subgraph that fetches news articles."""

import os
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from langgraph.graph import StateGraph, END
from models import ResearchState, NewsCard


def news_node(state: ResearchState) -> ResearchState:
    """
    Node that fetches news articles from NewsAPI.
    Searches for articles matching the user query and returns them as NewsCard objects.
    """
    try:
        user_query = state.user_query
        # lab_profile = state.lab_profile  # Can be used for filtering later

        # Initialize NewsAPI client
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            raise ValueError("NEWS_API_KEY not found in environment variables")

        newsapi = NewsApiClient(api_key=api_key)

        # Calculate date range (last 30 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)

        # Fetch news articles using everything endpoint for comprehensive search
        response = newsapi.get_everything(
            q=user_query,
            from_param=from_date.strftime("%Y-%m-%d"),
            to=to_date.strftime("%Y-%m-%d"),
            language="en",
            sort_by="relevancy",
            page_size=10,  # Fetch top 10 articles
        )

        news = []
        if response.get("status") == "ok" and response.get("articles"):
            for idx, article in enumerate(response["articles"]):
                # Calculate a simple relevance score (decreasing with position)
                # NewsAPI returns articles sorted by relevancy
                score = max(0.5, 0.95 - (idx * 0.05))

                # Parse published date
                published_date = None
                if article.get("publishedAt"):
                    try:
                        dt = datetime.fromisoformat(
                            article["publishedAt"].replace("Z", "+00:00")
                        )
                        published_date = dt.strftime("%Y-%m-%d")
                    except Exception:
                        published_date = article.get("publishedAt", "")[:10]

                # Determine if article is recent (within last 7 days)
                badge = None
                if published_date:
                    try:
                        pub_dt = datetime.strptime(published_date, "%Y-%m-%d")
                        days_ago = (datetime.now() - pub_dt).days
                        if days_ago <= 7:
                            badge = "Recent"
                        elif days_ago <= 1:
                            badge = "Breaking"
                    except Exception:
                        pass

                news_card = NewsCard.create(
                    title=article.get("title", "Untitled"),
                    score=score,
                    published_date=published_date,
                    outlet=article.get("source", {}).get("name", "Unknown"),
                    url=article.get("url"),
                    badge=badge,
                    source="newsapi",
                )
                news.append(news_card)

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
