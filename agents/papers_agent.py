"""Papers agent subgraph that fetches research papers."""

import time
import xml.etree.ElementTree as ET
from typing import Optional
from datetime import datetime

import requests
from langgraph.graph import StateGraph, END
from models import ResearchState, PaperCard


# Rate limiting: NCBI allows max 3 requests per second without API key
NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
MIN_REQUEST_INTERVAL = 0.34  # Slightly more than 1/3 second to ensure < 3/sec
_last_request_time: Optional[float] = None


def _rate_limit():
    """Ensure requests are spaced at least MIN_REQUEST_INTERVAL seconds apart."""
    global _last_request_time
    if _last_request_time is not None:
        elapsed = time.time() - _last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def _search_pubmed(query: str, max_results: int = 10) -> list[str]:
    """
    Search PubMed using ESearch and return list of PMIDs.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of PubMed IDs (PMIDs)
    """
    _rate_limit()

    params = {
        "db": "pubmed",
        "term": query,
        "retmax": str(max_results),
        "retmode": "xml",
        "tool": "mongo-research",
        "email": "developer@example.com",  # Should be registered with NCBI
    }

    response = requests.get(f"{NCBI_BASE_URL}/esearch.fcgi", params=params, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    id_elements = root.findall(".//Id")
    return [id_elem.text for id_elem in id_elements if id_elem.text is not None]


def _fetch_pubmed_details(pmids: list[str]) -> list[dict]:
    """
    Fetch detailed information for PubMed IDs using EFetch.

    Args:
        pmids: List of PubMed IDs

    Returns:
        List of dictionaries containing paper details
    """
    if not pmids:
        return []

    _rate_limit()

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml",
        "tool": "mongo-research",
        "email": "developer@example.com",
    }

    response = requests.get(f"{NCBI_BASE_URL}/efetch.fcgi", params=params, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    papers = []

    # Parse each article in the XML
    for article in root.findall(".//PubmedArticle"):
        paper_data = _parse_pubmed_article(article)
        if paper_data:
            papers.append(paper_data)

    return papers


def _parse_pubmed_article(article: ET.Element) -> Optional[dict]:
    """
    Parse a PubmedArticle XML element into a dictionary.

    Args:
        article: XML element representing a PubmedArticle

    Returns:
        Dictionary with paper details or None if parsing fails
    """
    try:
        # Extract title
        title_elem = article.find(".//ArticleTitle")
        title = (
            title_elem.text
            if title_elem is not None and title_elem.text
            else "No title"
        )

        # Extract authors
        authors = []
        for author in article.findall(".//Author"):
            lastname = author.find("LastName")
            firstname = author.find("ForeName")
            initials = author.find("Initials")

            if lastname is not None and lastname.text:
                name_parts = [lastname.text]
                if firstname is not None and firstname.text:
                    name_parts.append(firstname.text)
                elif initials is not None and initials.text:
                    name_parts.append(initials.text)
                authors.append(", ".join(name_parts))

        # Extract publication date
        # Try PubDate first (Journal publication date), then PubmedPubDate
        pub_date_elem = article.find(".//PubDate")
        if pub_date_elem is None:
            pub_date_elem = article.find(".//PubmedPubDate")

        published_date = None
        if pub_date_elem is not None:
            year_elem = pub_date_elem.find("Year")
            month_elem = pub_date_elem.find("Month")
            day_elem = pub_date_elem.find("Day")

            if year_elem is not None and year_elem.text:
                date_parts = [year_elem.text]
                month_num = None
                if month_elem is not None and month_elem.text:
                    month_text = month_elem.text.strip()
                    # Convert month name to number if needed
                    month_names = {
                        "Jan": "01",
                        "Feb": "02",
                        "Mar": "03",
                        "Apr": "04",
                        "May": "05",
                        "Jun": "06",
                        "Jul": "07",
                        "Aug": "08",
                        "Sep": "09",
                        "Oct": "10",
                        "Nov": "11",
                        "Dec": "12",
                    }
                    if month_text in month_names:
                        month_num = month_names[month_text]
                    elif month_text.isdigit():
                        month_num = month_text.zfill(2)
                    else:
                        # Try to parse as month name (full name)
                        for name, num in month_names.items():
                            if month_text.startswith(name):
                                month_num = num
                                break

                    if month_num:
                        date_parts.append(month_num)
                        if day_elem is not None and day_elem.text:
                            date_parts.append(day_elem.text.zfill(2))
                        else:
                            date_parts.append("01")
                    else:
                        date_parts.extend(["01", "01"])
                else:
                    date_parts.extend(["01", "01"])
                published_date = "-".join(date_parts)

        # Extract PMID for potential badge/citation info
        pmid_elem = article.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None and pmid_elem.text else None

        # Calculate a simple score based on recency (newer papers score higher)
        score = 0.5  # Base score
        if published_date:
            try:
                pub_dt = datetime.strptime(published_date[:10], "%Y-%m-%d")
                now = datetime.now()
                days_old = (now - pub_dt).days
                # Score decreases with age, max 2 years old gets minimum score
                if days_old < 365:
                    score = max(
                        0.5, 1.0 - (days_old / 730)
                    )  # Linear decay over 2 years
                else:
                    score = 0.5
            except (ValueError, TypeError):
                pass

        # Add badge for recent high-impact papers (example heuristic)
        badge = None
        if published_date:
            try:
                pub_dt = datetime.strptime(published_date[:10], "%Y-%m-%d")
                now = datetime.now()
                days_old = (now - pub_dt).days
                if days_old < 180:  # Less than 6 months old
                    badge = "Recent"
            except (ValueError, TypeError):
                pass

        return {
            "title": title,
            "score": min(1.0, max(0.0, score)),  # Ensure score is between 0 and 1
            "published_date": published_date,
            "authors": authors,
            "badge": badge,
            "source": "pubmed",
        }
    except Exception:
        return None


def papers_node(state: ResearchState) -> ResearchState:
    """
    Node that fetches research papers from PubMed using NCBI E-utilities API.

    Uses ESearch to find papers matching the user query, then EFetch to get details.
    Implements rate limiting to comply with NCBI's 3 requests/second limit.
    """
    try:
        user_query = state.user_query
        # lab_profile = state.lab_profile  # Can be used for filtering later

        if not user_query or not user_query.strip():
            # Empty query, return empty papers list
            state_dict = state.model_dump()
            state_dict["papers"] = []
            return ResearchState(**state_dict)

        # Search PubMed for papers matching the query
        pmids = _search_pubmed(user_query.strip(), max_results=10)

        if not pmids:
            # No results found
            state_dict = state.model_dump()
            state_dict["papers"] = []
            return ResearchState(**state_dict)

        # Fetch detailed information for the found papers
        paper_data_list = _fetch_pubmed_details(pmids)

        # Convert to PaperCard objects
        papers = []
        for paper_data in paper_data_list:
            try:
                paper_card = PaperCard.create(
                    title=paper_data["title"],
                    score=paper_data["score"],
                    published_date=paper_data.get("published_date"),
                    authors=paper_data.get("authors") or [],
                    badge=paper_data.get("badge"),
                    source=paper_data.get("source", "pubmed"),
                )
                papers.append(paper_card)
            except Exception as e:
                # Skip papers that fail to create (shouldn't happen, but be safe)
                continue

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
