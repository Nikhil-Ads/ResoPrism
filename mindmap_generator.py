"""
Mind Map Generator using OpenAI

Takes research results (grants, papers, news) and uses OpenAI to:
1. Find thematic similarities and connections
2. Generate a hierarchical markdown structure for markmap.js
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


class MindMapRequest(BaseModel):
    """Request model for mind map generation."""
    grants: list[dict] = Field(default_factory=list)
    papers: list[dict] = Field(default_factory=list)
    news: list[dict] = Field(default_factory=list)
    user_query: Optional[str] = Field(None, description="Original search query for context")


class MindMapResponse(BaseModel):
    """Response model for mind map generation."""
    markdown: str = Field(..., description="Markdown content for markmap.js")
    themes: list[str] = Field(default_factory=list, description="Identified themes")
    connections: list[dict] = Field(default_factory=list, description="Cross-type connections found")


MINDMAP_SYSTEM_PROMPT = """You are an expert research analyst who identifies patterns, themes, and connections across different types of research data (grants, papers, and news).

Your task is to analyze the provided research results and create a hierarchical mind map structure in Markdown format that can be rendered by markmap.js.

The markdown should:
1. Use the original query as the central/root topic
2. Identify 3-5 main themes that connect the grants, papers, and news
3. Under each theme, group relevant items from grants, papers, and news
4. Show cross-connections between different data types
5. Use proper markdown heading hierarchy (# for root, ## for themes, ### for categories, #### for items)

Format Rules:
- Use # for the central topic (root)
- Use ## for main themes/categories
- Use ### for sub-categories (Grants, Papers, News under each theme)
- Use #### or bullet points for individual items
- Keep item titles concise (max 50 chars, truncate with ... if needed)
- Add relevant metadata in parentheses when helpful

Example structure:
# Research Topic
## Theme 1: [Identified Theme]
### Grants
- Grant title 1 (Sponsor)
- Grant title 2 (Amount)
### Papers  
- Paper title 1 (Authors)
### News
- News title 1 (Source)
## Theme 2: [Another Theme]
...

Be insightful about the connections - don't just list items, actually identify meaningful thematic relationships."""


def generate_mindmap(
    grants: list[dict],
    papers: list[dict],
    news: list[dict],
    user_query: Optional[str] = None,
) -> MindMapResponse:
    """
    Generate a mind map from research results using OpenAI.
    
    Args:
        grants: List of grant cards
        papers: List of paper cards
        news: List of news cards
        user_query: Original search query for context
        
    Returns:
        MindMapResponse with markdown and identified themes
    """
    # Prepare the data summary for the LLM
    grants_summary = []
    for g in grants[:15]:  # Limit to top 15 for context window
        grants_summary.append({
            "title": g.get("title", "Unknown"),
            "sponsor": g.get("meta", {}).get("sponsor", "Unknown"),
            "amount": g.get("meta", {}).get("amount_max"),
            "close_date": g.get("meta", {}).get("close_date"),
            "score": g.get("score", 0)
        })
    
    papers_summary = []
    for p in papers[:15]:
        papers_summary.append({
            "title": p.get("title", "Unknown"),
            "authors": p.get("meta", {}).get("authors", [])[:3],  # First 3 authors
            "published_date": p.get("meta", {}).get("published_date"),
            "score": p.get("score", 0)
        })
    
    news_summary = []
    for n in news[:15]:
        news_summary.append({
            "title": n.get("title", "Unknown"),
            "outlet": n.get("meta", {}).get("outlet", "Unknown"),
            "published_date": n.get("meta", {}).get("published_date"),
            "score": n.get("score", 0)
        })
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", MINDMAP_SYSTEM_PROMPT),
        ("human", """Please analyze these research results and generate a mind map in Markdown format.

Original Search Query: {query}

=== GRANTS ({grants_count} total) ===
{grants_data}

=== PAPERS ({papers_count} total) ===
{papers_data}

=== NEWS ({news_count} total) ===
{news_data}

Generate a hierarchical markdown mind map that identifies themes and connections across these results. 
Also list the main themes you identified and any notable cross-type connections.

Respond in this JSON format:
{{
    "markdown": "# Your Markdown Here...",
    "themes": ["Theme 1", "Theme 2", ...],
    "connections": [
        {{"from_type": "grant", "to_type": "paper", "description": "Connection description"}},
        ...
    ]
}}""")
    ])
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Format the data
    import json
    grants_data = json.dumps(grants_summary, indent=2) if grants_summary else "No grants found"
    papers_data = json.dumps(papers_summary, indent=2) if papers_summary else "No papers found"
    news_data = json.dumps(news_summary, indent=2) if news_summary else "No news found"
    
    # Create the chain
    chain = prompt | llm
    
    # Invoke the chain
    response = chain.invoke({
        "query": user_query or "Research Results",
        "grants_count": len(grants),
        "papers_count": len(papers),
        "news_count": len(news),
        "grants_data": grants_data,
        "papers_data": papers_data,
        "news_data": news_data,
    })
    
    # Parse the response
    try:
        # Try to extract JSON from the response
        content = response.content
        
        # Find JSON in the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            result = json.loads(json_match.group())
            return MindMapResponse(
                markdown=result.get("markdown", "# No results"),
                themes=result.get("themes", []),
                connections=result.get("connections", [])
            )
        else:
            # If no JSON found, treat the entire response as markdown
            return MindMapResponse(
                markdown=content,
                themes=[],
                connections=[]
            )
    except json.JSONDecodeError:
        # Fallback: use the response as markdown directly
        return MindMapResponse(
            markdown=response.content,
            themes=[],
            connections=[]
        )


def generate_simple_mindmap(
    grants: list[dict],
    papers: list[dict],
    news: list[dict],
    user_query: Optional[str] = None,
) -> str:
    """
    Generate a simple hierarchical markdown without OpenAI analysis.
    Useful as a fallback or for quick visualization.
    
    Returns:
        Markdown string for markmap.js
    """
    query = user_query or "Research Results"
    
    lines = [f"# {query}"]
    
    if grants:
        lines.append("\n## 💰 Grants")
        for g in grants[:10]:
            title = g.get("title", "Unknown")[:50]
            sponsor = g.get("meta", {}).get("sponsor", "")
            if sponsor:
                lines.append(f"### {title}")
                lines.append(f"- Sponsor: {sponsor}")
            else:
                lines.append(f"### {title}")
    
    if papers:
        lines.append("\n## 📄 Papers")
        for p in papers[:10]:
            title = p.get("title", "Unknown")[:50]
            authors = p.get("meta", {}).get("authors", [])
            if authors:
                lines.append(f"### {title}")
                lines.append(f"- Authors: {', '.join(authors[:2])}")
            else:
                lines.append(f"### {title}")
    
    if news:
        lines.append("\n## 📰 News")
        for n in news[:10]:
            title = n.get("title", "Unknown")[:50]
            outlet = n.get("meta", {}).get("outlet", "")
            if outlet:
                lines.append(f"### {title}")
                lines.append(f"- Source: {outlet}")
            else:
                lines.append(f"### {title}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test with sample data
    test_grants = [
        {"title": "AI in Healthcare Research Grant", "meta": {"sponsor": "NIH", "amount_max": 500000}},
        {"title": "Machine Learning Drug Discovery", "meta": {"sponsor": "NSF", "amount_max": 250000}},
    ]
    test_papers = [
        {"title": "Deep Learning for Medical Imaging", "meta": {"authors": ["Smith J.", "Doe A."]}},
        {"title": "Neural Networks in Clinical Diagnosis", "meta": {"authors": ["Johnson B."]}},
    ]
    test_news = [
        {"title": "FDA Approves AI-based Diagnostic Tool", "meta": {"outlet": "Reuters"}},
        {"title": "Tech Giants Invest in Healthcare AI", "meta": {"outlet": "TechCrunch"}},
    ]
    
    # Test simple mindmap
    print("=== Simple Mindmap ===")
    simple_md = generate_simple_mindmap(test_grants, test_papers, test_news, "AI Healthcare")
    print(simple_md)
    
    # Test OpenAI mindmap (requires API key)
    print("\n=== OpenAI Mindmap ===")
    try:
        result = generate_mindmap(test_grants, test_papers, test_news, "AI Healthcare")
        print(result.markdown)
        print(f"\nThemes: {result.themes}")
        print(f"Connections: {result.connections}")
    except Exception as e:
        print(f"OpenAI test failed (expected if no API key): {e}")
