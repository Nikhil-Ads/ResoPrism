# MongoResearch - LangGraph Multi-Agent Research Inbox

A LangGraph-based multi-agent system that orchestrates research data collection from grants, papers, and news sources, returning ranked inbox cards suitable for a React UI.

## Features

- **Orchestrator Graph**: Routes user requests to specialized subagents based on intent
- **Subagent Graphs**: Three independent agents for grants, papers, and news
- **URL-Based Research**: Web scrape research lab URLs and extract keywords for API queries
- **LLM Keyword Extraction**: Uses OpenAI to extract research-relevant keywords from web content
- **MongoDB Caching**: Cache results to avoid redundant API calls for the same URLs
- **Real API Integrations**: Fetches data from grants.gov, PubMed (NCBI), and NewsAPI
- **Deterministic Ranking**: Cards ranked by score, type priority, and title
- **Error Resilience**: Partial results returned even if some agents fail
- **REST API**: FastAPI endpoints for easy integration

## Project Structure

```
MongoResearch/
├── orchestrator.py          # Main orchestrator graph
├── models.py                # Pydantic models (state + cards)
├── ranking.py               # Ranking logic
├── api.py                   # FastAPI server
├── web_scraper.py           # Web scraping module
├── keyword_extractor.py     # LLM-based keyword extraction
├── cache.py                 # MongoDB caching operations
├── url_research_service.py  # URL research orchestration
├── agents/                  # Subagent graphs and API clients
│   ├── grants_agent.py      # Grants subagent (stub)
│   ├── grants_api_client.py # Real grants.gov API client
│   ├── papers_agent.py      # Papers subagent (stub)
│   ├── pubmed_api_client.py # Real PubMed API client
│   ├── news_agent.py        # News subagent (stub)
│   └── news_api_client.py   # Real NewsAPI client
└── tests/                   # Test suite
```

## Installation

```bash
# Install dependencies
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=mongo_research

# NewsAPI Configuration
# Get your API key from https://newsapi.org/
NEWS_API_KEY=your_newsapi_key_here

# OpenAI Configuration (for LLM-based keyword extraction)
# Get your API key from https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Grants.gov API key (if authentication is required)
# GRANTS_API_KEY=your_grants_api_key_here
```

**Note**: If `OPENAI_API_KEY` is not set, the system will fall back to simple keyword extraction. If `NEWS_API_KEY` is not set, news results will be empty. MongoDB caching is optional - the system will continue to work without it, just without caching.

## Usage

### As a Python Module

```python
from orchestrator import ORCHESTRATOR
from models import ResearchState

# Create state
state = ResearchState(
    user_query="ml healthcare funding",
    intent="all"  # or "grants", "papers", "news"
)

# Invoke orchestrator
result = ORCHESTRATOR.invoke(state)

# Access results
print(f"Found {len(result['inbox_cards'])} cards")
for card in result['inbox_cards']:
    print(f"- {card['type']}: {card['title']} (score: {card['score']})")
```

### As an API Server

Start the FastAPI server:

```bash
python api.py
```

Or with uvicorn directly:

```bash
uvicorn api:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

#### API Endpoints

**POST /api/inbox**
```bash
curl -X POST "http://localhost:8000/api/inbox" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "ml healthcare funding",
    "intent": "all"
  }'
```

**GET /api/inbox**
```bash
curl "http://localhost:8000/api/inbox?user_query=ml%20healthcare%20funding&intent=all"
```

**POST /api/url-research** (New!)
```bash
curl -X POST "http://localhost:8000/api/url-research" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example-research-lab.edu"
  }'
```

This endpoint:
1. Web scrapes the provided URL
2. Extracts research-relevant keywords using LLM
3. Queries grants.gov, PubMed, and NewsAPI with those keywords
4. Caches results in MongoDB for future requests
5. Returns ranked results in the same format as `/api/inbox`

**API Documentation**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### Response Format

```json
{
  "user_query": "ml healthcare funding",
  "intent": "all",
  "grants": [...],
  "papers": [...],
  "news": [...],
  "inbox_cards": [
    {
      "id": "abc123...",
      "type": "grant",
      "title": "NSF Machine Learning Grant",
      "score": 0.85,
      "badge": "Closing soon",
      "meta": {
        "close_date": "2024-12-31",
        "amount_max": 500000.0,
        "sponsor": "NSF",
        "source": "grants.gov"
      }
    },
    ...
  ],
  "errors": []
}
```

## Supported Intents

- `"grants"`: Run only GrantsAgentGraph
- `"papers"`: Run only PapersAgentGraph
- `"news"`: Run only NewsAgentGraph
- `"all"` (default): Run all three agents

## Running Tests

```bash
pytest tests/ -v
```

## State Contract

**Input Fields:**
- `user_query` (str, required): Search query
- `intent` (str, optional): One of "grants", "papers", "news", "all"
- `lab_url` (str, optional): Lab URL
- `lab_profile` (dict, optional): Lab profile data

**Output Fields:**
- `grants` (list): Grant cards from GrantsAgentGraph
- `papers` (list): Paper cards from PapersAgentGraph
- `news` (list): News cards from NewsAgentGraph
- `inbox_cards` (list): Merged and ranked cards
- `errors` (list): Error messages

## Card Schema

Each card in `inbox_cards` has:
- `id` (str): Deterministic ID
- `type` (str): "grant" | "paper" | "news"
- `title` (str): Card title
- `score` (float): Relevance score (0-1)
- `badge` (str, optional): Badge text (e.g., "Closing soon")
- `meta` (dict): Type-specific metadata

## Ranking Rules

1. Primary: Score descending
2. Tie-breaker 1: Type priority (grant > paper > news)
3. Tie-breaker 2: Title alphabetical (ascending)

## API Integrations

The system integrates with the following APIs:

- **Grants.gov**: [Search API](https://www.grants.gov/api/common/search2)
- **PubMed/NCBI**: [E-utilities API](https://www.ncbi.nlm.nih.gov/home/develop/api/)
- **NewsAPI**: [Everything Endpoint](https://newsapi.org/docs/endpoints/everything)

URL-based research (`/api/url-research`) uses real API integrations with caching. The original `/api/inbox` endpoint still uses stub data for backwards compatibility.
