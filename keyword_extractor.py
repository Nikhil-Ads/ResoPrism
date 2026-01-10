"""Keyword extraction module using LLM for research-relevant keywords."""

import os
import re
import logging
from typing import List, Optional

try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)


def extract_research_keywords(content: str, max_keywords: int = 10) -> List[str]:
    """
    Extract research-relevant keywords from scraped content using LLM.
    Falls back to simple extraction if LLM is unavailable.
    
    Args:
        content: Scraped content text
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of keywords/phrases suitable for API queries
    """
    if not content or not content.strip():
        return []
    
    # Try LLM-based extraction first
    if LANGCHAIN_AVAILABLE:
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                return _extract_with_llm(content, max_keywords, api_key)
            else:
                logger.warning("OPENAI_API_KEY not set, falling back to simple extraction")
        except Exception as e:
            logger.warning(f"LLM extraction failed: {str(e)}, falling back to simple extraction")
    
    # Fallback to simple extraction
    return _extract_simple_keywords(content, max_keywords)


def _extract_with_llm(content: str, max_keywords: int, api_key: str) -> List[str]:
    """Extract keywords using OpenAI LLM."""
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=api_key,
            max_tokens=200,
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at identifying research-relevant keywords from academic and research lab websites.
Extract key research domains, methodologies, techniques, topics, and subject areas that would be useful for searching:
- Research grants (grants.gov)
- Academic papers (PubMed)
- Science news articles (NewsAPI)

Return only the keywords as a comma-separated list. Focus on:
- Specific research topics and fields
- Methodologies and techniques
- Domain-specific terms
- Avoid generic words like "research", "study", "analysis"

Return at most {max_keywords} keywords.""",
            ),
            ("human", "Extract research keywords from this content:\n\n{content}"),
        ])
        
        # Truncate content if too long (keep first 3000 chars)
        truncated_content = content[:3000] if len(content) > 3000 else content
        
        messages = prompt.format_messages(
            max_keywords=max_keywords,
            content=truncated_content
        )
        
        response = llm.invoke(messages)
        
        # Parse response - extract keywords from comma-separated list
        # Handle different response formats (content vs text attribute)
        if hasattr(response, 'content'):
            keywords_text = response.content.strip()
        elif hasattr(response, 'text'):
            keywords_text = response.text.strip()
        else:
            keywords_text = str(response).strip()
        
        # Split by comma and clean up
        keywords = [
            kw.strip() 
            for kw in keywords_text.split(",") 
            if kw.strip() and len(kw.strip()) > 2
        ]
        
        # Limit to max_keywords
        keywords = keywords[:max_keywords]
        
        logger.info(f"Extracted {len(keywords)} keywords using LLM")
        return keywords
        
    except Exception as e:
        logger.error(f"Error in LLM extraction: {str(e)}")
        raise


def _extract_simple_keywords(content: str, max_keywords: int) -> List[str]:
    """
    Simple keyword extraction fallback using heuristics.
    Extracts meaningful phrases and terms.
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', content)
    
    # Extract capitalized phrases (likely proper nouns or important terms)
    capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    # Extract technical terms (words with 5+ chars, not common stop words)
    stop_words = {
        'this', 'that', 'with', 'from', 'have', 'been', 'will', 'which',
        'their', 'there', 'these', 'those', 'about', 'after', 'before',
        'research', 'study', 'analysis', 'method', 'result', 'conclusion'
    }
    
    words = re.findall(r'\b[a-z]{5,}\b', text.lower())
    meaningful_words = [w for w in words if w not in stop_words]
    
    # Combine and deduplicate
    keywords = list(set(capitalized_phrases + meaningful_words))
    
    # Sort by length (longer phrases first, as they're more specific)
    keywords.sort(key=len, reverse=True)
    
    # Limit to max_keywords
    keywords = keywords[:max_keywords]
    
    logger.info(f"Extracted {len(keywords)} keywords using simple extraction")
    return keywords
