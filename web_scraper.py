"""Web scraping module for extracting content from research lab URLs."""

import httpx
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def scrape_url(url: str, timeout: int = 30) -> Dict[str, str]:
    """
    Scrape content from a URL and extract structured text.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with extracted content:
        - title: Page title
        - headings: Combined headings (h1-h6)
        - meta_description: Meta description tag content
        - main_content: Main body text
        - full_text: Combined full text
        
    Raises:
        httpx.HTTPError: For HTTP errors
        ValueError: For invalid URLs
    """
    try:
        # Validate URL format
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "lxml")
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.get_text(strip=True)
            
            # Extract meta description
            meta_description = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if not meta_tag:
                meta_tag = soup.find("meta", attrs={"property": "og:description"})
            if meta_tag:
                meta_description = meta_tag.get("content", "").strip()
            
            # Extract headings (h1-h6)
            headings = []
            for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                heading_text = tag.get_text(strip=True)
                if heading_text:
                    headings.append(heading_text)
            headings_text = " ".join(headings)
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract main content - try to find main/article/content sections
            main_content = ""
            main_tag = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
            if main_tag:
                main_content = main_tag.get_text(separator=" ", strip=True)
            else:
                # Fallback to body text
                body = soup.find("body")
                if body:
                    main_content = body.get_text(separator=" ", strip=True)
            
            # Combine all text for full content
            full_text = " ".join(filter(None, [title, meta_description, headings_text, main_content]))
            
            return {
                "title": title,
                "headings": headings_text,
                "meta_description": meta_description,
                "main_content": main_content[:5000],  # Limit main content size
                "full_text": full_text[:10000],  # Limit full text for keyword extraction
            }
            
    except httpx.TimeoutException:
        logger.error(f"Timeout while scraping URL: {url}")
        raise ValueError(f"Request timeout for URL: {url}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} while scraping URL: {url}")
        raise ValueError(f"HTTP {e.response.status_code} error for URL: {url}")
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}")
        raise ValueError(f"Failed to scrape URL: {url}. Error: {str(e)}")
