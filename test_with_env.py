"""Test URL research with environment variables loaded from .env file."""

import os
import sys

# Load .env file manually
try:
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    print("✓ Loaded environment variables from .env file")
except FileNotFoundError:
    print("⚠ .env file not found, using environment variables from shell")

# Now import and test
from url_research_service import process_url_research
import json

print("=" * 80)
print("ENVIRONMENT VARIABLES CHECK")
print("=" * 80)
news_key = os.getenv('NEWS_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')
mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')

print(f"NEWS_API_KEY: {'✓ Set (' + str(len(news_key)) + ' chars)' if news_key else '✗ Not set'}")
print(f"OPENAI_API_KEY: {'✓ Set (' + str(len(openai_key)) + ' chars)' if openai_key else '✗ Not set'}")
print(f"MONGODB_URI: {mongodb_uri}")

print("\n" + "=" * 80)
print("RUNNING URL RESEARCH FOR HANSEN LAB")
print("=" * 80)

url = "https://research.childrenshospital.org/research-units/hansen-lab-research"
print(f"URL: {url}\n")

result = process_url_research(url)

print("=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)
print(f"✓ Grants found: {len(result.get('grants', []))}")
print(f"✓ Papers found: {len(result.get('papers', []))}")
print(f"✓ News found: {len(result.get('news', []))}")
print(f"✓ Total inbox cards: {len(result.get('inbox_cards', []))}")
print(f"✓ Errors: {len(result.get('errors', []))}")

keywords = result.get('lab_profile', {}).get('keywords', [])
print(f"\n✓ Keywords extracted: {len(keywords)}")
print("\nExtracted Keywords:")
print("-" * 80)
for i, kw in enumerate(keywords, 1):
    print(f"  {i:2}. {kw}")

print("\n" + "=" * 80)
print("DETAILED RESULTS")
print("=" * 80)

# Show grants
if result.get('grants'):
    print(f"\n📋 GRANTS ({len(result['grants'])}):")
    print("-" * 80)
    for i, grant in enumerate(result['grants'][:10], 1):
        print(f"\n{i}. {grant.get('title', 'N/A')}")
        print(f"   Score: {grant.get('score', 0):.2f}")
        if grant.get('badge'):
            print(f"   Badge: {grant.get('badge')}")
        meta = grant.get('meta', {})
        if meta.get('sponsor'):
            print(f"   Sponsor: {meta['sponsor']}")
        if meta.get('close_date'):
            print(f"   Close Date: {meta['close_date']}")
        if meta.get('amount_max'):
            print(f"   Amount: ${meta['amount_max']:,.0f}")
else:
    print("\n📋 GRANTS: None found")

# Show papers
if result.get('papers'):
    print(f"\n📄 PAPERS ({len(result['papers'])}):")
    print("-" * 80)
    for i, paper in enumerate(result['papers'][:10], 1):
        print(f"\n{i}. {paper.get('title', 'N/A')}")
        print(f"   Score: {paper.get('score', 0):.2f}")
        if paper.get('badge'):
            print(f"   Badge: {paper.get('badge')}")
        meta = paper.get('meta', {})
        if meta.get('published_date'):
            print(f"   Published: {meta['published_date']}")
        if meta.get('authors'):
            authors = meta['authors'][:3]
            print(f"   Authors: {', '.join(authors)}{'...' if len(meta['authors']) > 3 else ''}")
else:
    print("\n📄 PAPERS: None found")

# Show news
if result.get('news'):
    print(f"\n📰 NEWS ({len(result['news'])}):")
    print("-" * 80)
    for i, news in enumerate(result['news'][:10], 1):
        print(f"\n{i}. {news.get('title', 'N/A')}")
        print(f"   Score: {news.get('score', 0):.2f}")
        if news.get('badge'):
            print(f"   Badge: {news.get('badge')}")
        meta = news.get('meta', {})
        if meta.get('published_date'):
            print(f"   Published: {meta['published_date']}")
        if meta.get('outlet'):
            print(f"   Outlet: {meta['outlet']}")
        if meta.get('url'):
            print(f"   URL: {meta['url'][:80]}...")
else:
    print("\n📰 NEWS: None found")

# Show errors
if result.get('errors'):
    print(f"\n⚠️  ERRORS ({len(result['errors'])}):")
    print("-" * 80)
    for error in result['errors']:
        print(f"  • {error}")

print("\n" + "=" * 80)
print("FULL JSON RESPONSE")
print("=" * 80)
print(json.dumps({
    "user_query": result.get("user_query"),
    "lab_url": result.get("lab_url"),
    "keywords_count": len(keywords),
    "grants_count": len(result.get('grants', [])),
    "papers_count": len(result.get('papers', [])),
    "news_count": len(result.get('news', [])),
    "total_cards": len(result.get('inbox_cards', [])),
    "errors": result.get('errors', [])
}, indent=2))

print("\n" + "=" * 80)
print("COMPLETE!")
print("=" * 80)
