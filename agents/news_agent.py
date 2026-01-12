"""News agent subgraph that fetches news articles."""

import os
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from langgraph.graph import StateGraph, END
from models import ResearchState, NewsCard
from research_retriever import ResearchRetriever


def news_node(state: ResearchState) -> ResearchState:
    """
    Node that fetches news articles from MongoDB vector search first,
    then falls back to NewsAPI if no results are found.
    Searches for articles matching the user query and returns them as NewsCard objects.
    """
    try:
        user_query = state.user_query
        news = []
        
        # Try MongoDB vector search first
        print(f"[News Agent] Attempting MongoDB vector search for query: '{user_query}'")
        try:
            retriever = ResearchRetriever()
            mongo_results = retriever.search_news(user_query, limit=10)
            
            if mongo_results:
                print(f"[News Agent] [OK] MongoDB returned {len(mongo_results)} results - using MongoDB data")
                # Transform MongoDB results to NewsCard objects
                for item in mongo_results:
                    title = item.get("title") or "Untitled"
                    score = item.get("score", 0.5)  # Use vectorSearchScore
                    meta = item.get("meta", {})
                    
                    # Extract fields from meta dict
                    published_date = meta.get("published_date")
                    outlet = meta.get("outlet") or meta.get("source_name")
                    url = meta.get("url")
                    badge = meta.get("badge")
                    
                    # If badge not in meta, determine it from published_date
                    if not badge and published_date:
                        try:
                            pub_dt = datetime.strptime(published_date, "%Y-%m-%d")
                            days_ago = (datetime.now() - pub_dt).days
                            if days_ago <= 1:
                                badge = "Breaking"
                            elif days_ago <= 7:
                                badge = "Recent"
                        except Exception:
                            pass
                    
                    news_card = NewsCard.create(
                        title=title,
                        score=min(1.0, max(0.0, score)),  # Ensure score is between 0 and 1
                        published_date=published_date,
                        outlet=outlet,
                        url=url,
                        badge=badge,
                        source="mongodb",
                    )
                    news.append(news_card)
                print(f"[News Agent] [OK] Successfully created {len(news)} news cards from MongoDB")
        except Exception as mongo_error:
            # If MongoDB search fails, fall through to API fallback
            print(f"[News Agent] [X] MongoDB search failed: {str(mongo_error)}")
            print(f"[News Agent] -> Falling back to NewsAPI")
        
        # Fall back to NewsAPI if no results from MongoDB
        if not news:
            print(f"[News Agent] [X] MongoDB returned 0 results")
            print(f"[News Agent] -> Falling back to NewsAPI")
            # Initialize NewsAPI client
            print(f"[News Agent] Fetching from NewsAPI...")
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
            
            if news:
                print(f"[News Agent] [OK] Successfully fetched {len(news)} news articles from NewsAPI")

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
