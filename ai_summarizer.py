"""AI-powered summary generation for grants, papers, and news sectors."""

import os
from typing import List, Literal
from models import GrantCard, PaperCard, NewsCard

# Try to import LLM dependencies, but make them optional
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    LLM_AVAILABLE = True
except ImportError:
    try:
        # Fallback: try importing from langchain directly (older versions)
        from langchain.chat_models import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate
        LLM_AVAILABLE = True
    except ImportError:
        LLM_AVAILABLE = False


def generate_sector_summary(
    results: List[GrantCard | PaperCard | NewsCard], 
    sector: Literal["grants", "papers", "news"],
    lab_profile: dict = None
) -> str:
    """
    Generate a personalized AI summary for a specific sector based on lab profile.
    
    Args:
        results: List of cards (grants, papers, or news) for this sector
        sector: The sector type ("grants", "papers", or "news")
        lab_profile: Optional lab profile dictionary with lab information
        
    Returns:
        Formatted summary text focusing on relevance and importance to the lab
    """
    if not LLM_AVAILABLE:
        return _generate_fallback_summary(results, sector, lab_profile)
    
    try:
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return _generate_fallback_summary(results, sector, lab_profile)
        
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        
        # Prepare results context (limit to avoid token limits)
        results_text = _format_results_for_prompt(results, sector)
        
        # Format lab profile for prompt
        lab_profile_text = _format_lab_profile_for_prompt(lab_profile) if lab_profile else ""
        
        # Create sector-specific prompt
        prompt_template = _get_sector_prompt(sector)
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_template["system"]),
            ("human", prompt_template["human"])
        ])
        
        # Create chain and invoke
        chain = prompt | llm
        response = chain.invoke({
            "results": results_text,
            "count": len(results),
            "lab_profile": lab_profile_text
        })
        
        # Extract content
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
            
    except Exception as e:
        print(f"AI summary generation failed: {e}, falling back to simple summary")
        return _generate_fallback_summary(results, sector, lab_profile)


def _format_results_for_prompt(
    results: List[GrantCard | PaperCard | NewsCard], 
    sector: Literal["grants", "papers", "news"]
) -> str:
    """Format results into a text string for the prompt."""
    if not results:
        return "No results found for this sector."
    
    # Limit to top 10 results to avoid token limits
    limited_results = results[:10]
    formatted_items = []
    
    for i, card in enumerate(limited_results, 1):
        if sector == "grants":
            grant_card = card  # type: ignore
            item_text = f"{i}. {grant_card.title}"
            if grant_card.meta.get("sponsor"):
                item_text += f" (Sponsor: {grant_card.meta['sponsor']})"
            if grant_card.meta.get("close_date"):
                item_text += f" [Deadline: {grant_card.meta['close_date']}]"
            if grant_card.meta.get("amount_max"):
                item_text += f" [Max Amount: ${grant_card.meta['amount_max']:,.0f}]"
            if grant_card.badge:
                item_text += f" [{grant_card.badge}]"
            formatted_items.append(item_text)
            
        elif sector == "papers":
            paper_card = card  # type: ignore
            item_text = f"{i}. {paper_card.title}"
            if paper_card.meta.get("authors"):
                authors = paper_card.meta["authors"]
                if isinstance(authors, list) and len(authors) > 0:
                    authors_str = ", ".join(authors[:3])  # Limit to first 3 authors
                    if len(authors) > 3:
                        authors_str += " et al."
                    item_text += f" by {authors_str}"
            if paper_card.meta.get("published_date"):
                item_text += f" ({paper_card.meta['published_date']})"
            formatted_items.append(item_text)
            
        elif sector == "news":
            news_card = card  # type: ignore
            item_text = f"{i}. {news_card.title}"
            if news_card.meta.get("outlet"):
                item_text += f" - {news_card.meta['outlet']}"
            if news_card.meta.get("published_date"):
                item_text += f" ({news_card.meta['published_date']})"
            formatted_items.append(item_text)
    
    return "\n".join(formatted_items)


def _format_lab_profile_for_prompt(lab_profile: dict) -> str:
    """Format lab profile into a text string for the prompt."""
    if not lab_profile:
        return ""
    
    parts = []
    
    if lab_profile.get("lab_name"):
        parts.append(f"Lab Name: {lab_profile['lab_name']}")
    
    if lab_profile.get("lab_description"):
        parts.append(f"Lab Description: {lab_profile['lab_description']}")
    
    if lab_profile.get("lab_focus"):
        parts.append(f"Lab Focus: {lab_profile['lab_focus']}")
    
    if lab_profile.get("research_areas"):
        parts.append("Research Areas:")
        for area in lab_profile["research_areas"]:
            if isinstance(area, dict):
                if area.get("category"):
                    parts.append(f"  - {area['category']}")
                    if area.get("topics"):
                        for topic in area["topics"]:
                            parts.append(f"    * {topic}")
    
    if lab_profile.get("keywords"):
        keywords_str = ", ".join(lab_profile["keywords"])
        parts.append(f"Keywords: {keywords_str}")
    
    return "\n".join(parts)


def _get_sector_prompt(sector: Literal["grants", "papers", "news"]) -> dict:
    """Get the prompt template for a specific sector."""
    
    if sector == "grants":
        return {
            "system": "You are a calm, competent research assistant who has reviewed grant opportunities and filtered them based on relevance to a specific lab. Write in a thoughtful, understated tone - like someone who actually skimmed the content and is sharing what matters. No hype, no AI magic, no emojis. Sound like you filtered this because it matters to them.",
            "human": """I found {count} grant opportunities. Here are the results:

{results}

Lab Profile:
{lab_profile}

Write a brief, thoughtful paragraph (3-4 sentences) that:
1. Starts with something like "I flagged these grants because they closely match your lab's research focus" - mention their lab specifically
2. If any grants are closing soon, mention it naturally: "A couple of them are approaching their deadlines and look realistically competitive based on prior award patterns"
3. For high-impact/large funding grants: "This is a high-impact opportunity with fewer awards, but labs with similar profiles to yours have been funded in previous cycles"
4. For early-career/pilot grants: "This looks well-suited for exploratory or pilot work and could be a good fit if you're planning a smaller, focused proposal"
5. If a grant is closing soon: "This one is closing soon, but it aligns unusually well with your current work. If you already have a proposal outline, this could be a strong short-term opportunity"
6. Be honest about competitiveness - don't oversell. Build trust by being realistic.
7. Do NOT mention search queries, AI, or how you found these. Just talk about the grants and why they matter to this lab.

Tone: Calm, competent, assistant-like. Sounds like someone who actually skimmed the content. Slightly thoughtful, not verbose. Feels like "I filtered this because it matters to you."

End with a subtle closing line like: "If you'd like, I can narrow future updates further or prioritize things with upcoming deadlines or higher likelihood of fit." Or: "Let me know if you want this tuned more toward grants, papers, or broader field updates." This reinforces control, personalization, and long-term assistant behavior."""
        }
    
    elif sector == "papers":
        return {
            "system": "You are a calm, competent research assistant who has reviewed research papers and selected them based on relevance to a specific lab. Write in a thoughtful, understated tone - like someone who actually skimmed the content and is sharing what matters. No hype, no AI magic, no emojis. Sound like you filtered this because it matters to them.",
            "human": """I found {count} relevant research papers. Here are the results:

{results}

Lab Profile:
{lab_profile}

Write a brief, thoughtful paragraph (3-4 sentences) that:
1. Starts with something like "These papers were selected because they overlap with your lab's recent topics and methods" - mention methods, not just keywords
2. For directly relevant papers: "This paper stood out as especially relevant to your lab's work — it builds on a similar problem space and may be useful for framing or comparison"
3. For trending/highly cited papers: "This paper is gaining attention in your field and may be useful for staying current with how the topic is being discussed right now" - frame value as awareness, not obligation
4. For exploratory papers: "This one is slightly adjacent to your core focus, but it introduces ideas that could be useful if you're exploring new directions"
5. Imply understanding of research depth - mention methods and approaches, not just keywords
6. Do NOT mention search queries, AI, or how you found these. Just talk about the papers and why they matter to this lab.

Tone: Calm, competent, assistant-like. Sounds like someone who actually skimmed the content. Slightly thoughtful, not verbose. Feels like "I filtered this because it matters to you."

End with a subtle closing line like: "If you'd like, I can narrow future updates further or prioritize things with upcoming deadlines or higher likelihood of fit." Or: "Let me know if you want this tuned more toward grants, papers, or broader field updates." This reinforces control, personalization, and long-term assistant behavior."""
        }
    
    else:  # news
        return {
            "system": "You are a calm, competent research assistant who has reviewed news articles and selected them based on relevance to a specific lab. Write in a thoughtful, understated tone - like someone who actually skimmed the content and is sharing what matters. No hype, no AI magic, no emojis. Sound like you filtered this because it matters to them.",
            "human": """I found {count} relevant news articles. Here are the results:

{results}

Lab Profile:
{lab_profile}

Write a brief, thoughtful paragraph (3-4 sentences) that:
1. Starts with something like "These updates reflect recent developments in your field that may affect funding priorities, collaboration opportunities, or upcoming calls" - tie news to real research consequences, not just headlines
2. For policy/funding news: "This update could influence future funding calls or review priorities, so it's worth keeping on your radar"
3. For industry/collaboration news: "This may be relevant if you're considering industry collaborations or translational directions in the near future"
4. For trend/directional news: "This signals a broader shift in how this area is evolving, which could be useful context for future proposals or framing"
5. Connect news to real research consequences - funding priorities, collaboration opportunities, upcoming calls
6. Do NOT mention search queries, AI, or how you found these. Just talk about the news and why it matters to this lab.

Tone: Calm, competent, assistant-like. Sounds like someone who actually skimmed the content. Slightly thoughtful, not verbose. Feels like "I filtered this because it matters to you."

End with a subtle closing line like: "If you'd like, I can narrow future updates further or prioritize things with upcoming deadlines or higher likelihood of fit." Or: "Let me know if you want this tuned more toward grants, papers, or broader field updates." This reinforces control, personalization, and long-term assistant behavior."""
        }


def _generate_fallback_summary(
    results: List[GrantCard | PaperCard | NewsCard],
    sector: Literal["grants", "papers", "news"],
    lab_profile: dict = None
) -> str:
    """Generate a simple fallback summary when AI is unavailable."""
    count = len(results)
    
    if count == 0:
        return f"I didn't find any {sector} that match your research focus. Let me know if you'd like me to adjust the search criteria."
    
    if sector == "grants":
        summary = f"I flagged {count} grant opportunities that closely match your lab's research focus. "
        summary += "A couple of them may be approaching their deadlines and look realistically competitive."
        return summary
    
    elif sector == "papers":
        summary = f"These {count} papers were selected because they overlap with your lab's recent topics and methods. "
        summary += "One of them may introduce an approach that could be relevant to your current direction."
        return summary
    
    else:  # news
        summary = f"These {count} updates reflect recent developments in your field that may affect funding priorities or collaboration opportunities. "
        summary += "Worth keeping on your radar."
        return summary
