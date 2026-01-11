"""Keyword extraction module for extracting top keywords from text chunks."""

import os
import re
from typing import List
from collections import Counter

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


def extract_keywords_simple(text_chunks: List[str], top_k: int = 5) -> List[str]:
    """
    Extract top K keywords from text chunks using a simple TF-based approach.
    Falls back to this if LLM extraction fails.
    
    Args:
        text_chunks: List of text chunks
        top_k: Number of top keywords to extract
        
    Returns:
        List of top keywords sorted by relevance
    """
    # Combine all chunks
    combined_text = " ".join(text_chunks).lower()
    
    # Remove common stop words
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
        "been", "have", "has", "had", "do", "does", "did", "will", "would",
        "should", "could", "may", "might", "must", "can", "this", "that",
        "these", "those", "i", "you", "he", "she", "it", "we", "they", "what",
        "which", "who", "when", "where", "why", "how", "all", "each", "every",
        "both", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        "now"
    }
    
    # Extract words (alphanumeric sequences of 3+ characters)
    words = re.findall(r'\b[a-z]{3,}\b', combined_text)
    
    # Filter out stop words and count frequencies
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    word_counts = Counter(filtered_words)
    
    # Get top K keywords
    top_keywords = [word for word, count in word_counts.most_common(top_k)]
    
    return top_keywords


def extract_keywords_llm(text_chunks: List[str], top_k: int = 5) -> List[str]:
    """
    Extract top K keywords from text chunks using LLM.
    
    Args:
        text_chunks: List of text chunks
        top_k: Number of top keywords to extract
        
    Returns:
        List of top keywords sorted by relevance
    """
    if not LLM_AVAILABLE:
        # LLM dependencies not available, fall back to simple extraction
        return extract_keywords_simple(text_chunks, top_k)
    
    try:
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Fall back to simple extraction
            return extract_keywords_simple(text_chunks, top_k)
        
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Combine chunks (limit to avoid token limits)
        combined_text = " ".join(text_chunks)[:10000]  # Limit to ~10k chars
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a keyword extraction expert. Extract the top {top_k} most relevant and important keywords or key phrases from the given text. Return only the keywords, one per line, without numbering or bullets."),
            ("human", "Text:\n\n{text}\n\nExtract the top {top_k} most relevant keywords:")
        ])
        
        # Create chain
        chain = prompt | llm
        
        # Invoke chain
        response = chain.invoke({
            "text": combined_text,
            "top_k": top_k
        })
        
        # Parse response
        keywords = []
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
        
        # Extract keywords from response (one per line)
        lines = content.strip().split('\n')
        for line in lines:
            # Remove numbering, bullets, and clean up
            cleaned = re.sub(r'^[\d\.\-\*\s]+', '', line.strip())
            cleaned = cleaned.strip('"\'')
            if cleaned and len(cleaned) > 2:
                keywords.append(cleaned)
        
        # Limit to top_k and return
        return keywords[:top_k] if keywords else extract_keywords_simple(text_chunks, top_k)
        
    except Exception as e:
        # On any error, fall back to simple extraction
        print(f"LLM keyword extraction failed: {e}, falling back to simple extraction")
        return extract_keywords_simple(text_chunks, top_k)


def extract_top_keywords(text_chunks: List[str], top_k: int = 5, use_llm: bool = True) -> List[str]:
    """
    Extract top K keywords from text chunks.
    
    Args:
        text_chunks: List of text chunks
        top_k: Number of top keywords to extract (default: 5)
        use_llm: Whether to use LLM for extraction (default: True, falls back to simple if fails)
        
    Returns:
        List of top keywords sorted by relevance
    """
    if not text_chunks or len(text_chunks) == 0:
        return []
    
    # Filter out empty chunks
    valid_chunks = [chunk.strip() for chunk in text_chunks if chunk and chunk.strip()]
    if not valid_chunks:
        return []
    
    if use_llm:
        return extract_keywords_llm(valid_chunks, top_k)
    else:
        return extract_keywords_simple(valid_chunks, top_k)
