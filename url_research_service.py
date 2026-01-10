"""Main service module for URL-based research."""

import logging
from typing import Dict, Any, List
from web_scraper import scrape_url
from keyword_extractor import extract_research_keywords
from cache import get_cached_results, save_to_cache
from agents.grants_api_client import fetch_grants
from agents.pubmed_api_client import fetch_papers
from agents.news_api_client import fetch_news
from models import GrantCard, PaperCard, NewsCard, ResearchState, InboxCard
from ranking import rank_cards

logger = logging.getLogger(__name__)


def process_url_research(url: str) -> Dict[str, Any]:
    """
    Process URL research: scrape, extract keywords, fetch APIs, cache results.
    
    Args:
        url: Research lab URL to analyze
        
    Returns:
        Dictionary matching ResearchState schema with grants, papers, news, inbox_cards
    """
    errors = []
    
    try:
        # Step 1: Check cache first
        logger.info(f"Processing URL research for: {url}")
        cached_results = get_cached_results(url)
        
        if cached_results:
            logger.info("Returning cached results")
            # Convert cached results back to model objects
            grants = [GrantCard(**g) for g in cached_results.get("grants", [])]
            papers = [PaperCard(**p) for p in cached_results.get("papers", [])]
            news = [NewsCard(**n) for n in cached_results.get("news", [])]
            keywords = cached_results.get("keywords", [])
        else:
            logger.info("Cache miss - fetching fresh data")
            
            # Step 2: Scrape URL
            try:
                scraped_content = scrape_url(url)
                full_text = scraped_content.get("full_text", "")
                
                if not full_text or not full_text.strip():
                    errors.append("No content extracted from URL")
                    logger.warning(f"No content extracted from URL: {url}")
                    # Return empty results
                    return _create_empty_response(errors)
                    
            except Exception as e:
                error_msg = f"Error scraping URL: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                return _create_empty_response(errors)
            
            # Step 3: Extract keywords using LLM
            try:
                keywords = extract_research_keywords(full_text, max_keywords=10)
                
                if not keywords:
                    logger.warning("No keywords extracted, using fallback")
                    # Use a simple fallback - extract from title/headings
                    keywords = _extract_fallback_keywords(scraped_content)
                    
            except Exception as e:
                error_msg = f"Error extracting keywords: {str(e)}"
                logger.warning(error_msg)
                # Use fallback keywords
                keywords = _extract_fallback_keywords(scraped_content)
            
            # Step 4: Fetch data from APIs (run in parallel would be better, but sequential for simplicity)
            grants = []
            papers = []
            news = []
            
            # Fetch grants
            try:
                grants = fetch_grants(keywords, max_results=10)
            except Exception as e:
                error_msg = f"Error fetching grants: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
            
            # Fetch papers
            try:
                papers = fetch_papers(keywords, max_results=10)
            except Exception as e:
                error_msg = f"Error fetching papers: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
            
            # Fetch news
            try:
                news = fetch_news(keywords, max_results=10)
            except Exception as e:
                error_msg = f"Error fetching news: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
            
            # Step 5: Save to cache
            try:
                save_to_cache(url, keywords, grants, papers, news)
            except Exception as e:
                # Don't fail if caching fails, just log
                logger.warning(f"Failed to save to cache: {str(e)}")
        
        # Step 6: Merge and rank results
        inbox_cards: List[InboxCard] = []
        inbox_cards.extend(grants)
        inbox_cards.extend(papers)
        inbox_cards.extend(news)
        
        # Rank cards using existing ranking module
        try:
            ranked_cards = rank_cards(inbox_cards)
        except Exception as e:
            error_msg = f"Error ranking cards: {str(e)}"
            logger.warning(error_msg)
            ranked_cards = inbox_cards  # Use unranked if ranking fails
        
        # Step 7: Create response matching ResearchState schema
        result = {
            "user_query": f"Research for URL: {url}",
            "intent": "all",
            "lab_url": url,
            "lab_profile": {"keywords": keywords},
            "grants": [g.model_dump() if hasattr(g, "model_dump") else g for g in grants],
            "papers": [p.model_dump() if hasattr(p, "model_dump") else p for p in papers],
            "news": [n.model_dump() if hasattr(n, "model_dump") else n for n in news],
            "inbox_cards": [c.model_dump() if hasattr(c, "model_dump") else c for c in ranked_cards],
            "errors": errors,
        }
        
        logger.info(f"Processed URL research: {len(grants)} grants, {len(papers)} papers, {len(news)} news")
        return result
        
    except Exception as e:
        error_msg = f"Unexpected error processing URL research: {str(e)}"
        logger.error(error_msg, exc_info=True)
        errors.append(error_msg)
        return _create_empty_response(errors)


def _create_empty_response(errors: List[str]) -> Dict[str, Any]:
    """Create an empty response dictionary with errors."""
    return {
        "user_query": "",
        "intent": "all",
        "lab_url": None,
        "lab_profile": None,
        "grants": [],
        "papers": [],
        "news": [],
        "inbox_cards": [],
        "errors": errors,
    }


def _extract_fallback_keywords(scraped_content: Dict[str, str]) -> List[str]:
    """Extract simple keywords from scraped content as fallback."""
    keywords = []
    
    # Use title and headings
    title = scraped_content.get("title", "")
    headings = scraped_content.get("headings", "")
    
    # Extract words from title and headings
    import re
    text = f"{title} {headings}".lower()
    # Extract capitalized words and phrases
    words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', f"{title} {headings}")
    keywords.extend(words[:10])  # Limit to 10
    
    # If still not enough, extract meaningful words
    if len(keywords) < 5:
        all_words = re.findall(r'\b[a-z]{5,}\b', text)
        keywords.extend(all_words[:10 - len(keywords)])
    
    # Deduplicate and return
    return list(set(keywords))[:10]
