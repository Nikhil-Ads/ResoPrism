"""Test script for URL-based research endpoint."""

import asyncio
import json
from url_research_service import process_url_research

# Hansen Lab URL for testing
HANSEN_LAB_URL = "https://research.childrenshospital.org/research-units/hansen-lab-research"


def test_url_research():
    """Test the URL research service with Hansen Lab URL."""
    print(f"Testing URL Research Service with: {HANSEN_LAB_URL}\n")
    print("=" * 80)
    
    try:
        # Process the URL
        print("\n1. Processing URL...")
        result = process_url_research(HANSEN_LAB_URL)
        
        print("\n2. Results Summary:")
        print(f"   - Grants found: {len(result.get('grants', []))}")
        print(f"   - Papers found: {len(result.get('papers', []))}")
        print(f"   - News articles found: {len(result.get('news', []))}")
        print(f"   - Total inbox cards: {len(result.get('inbox_cards', []))}")
        print(f"   - Errors: {len(result.get('errors', []))}")
        
        # Show extracted keywords if available
        if result.get('lab_profile', {}).get('keywords'):
            keywords = result['lab_profile']['keywords']
            print(f"\n3. Extracted Keywords ({len(keywords)}):")
            for i, keyword in enumerate(keywords[:10], 1):
                print(f"   {i}. {keyword}")
        
        # Show sample results
        print("\n4. Sample Results:")
        
        # Show first grant
        if result.get('grants'):
            grant = result['grants'][0]
            print(f"\n   Grant: {grant.get('title', 'N/A')}")
            print(f"   Score: {grant.get('score', 0):.2f}")
            if grant.get('meta'):
                print(f"   Sponsor: {grant['meta'].get('sponsor', 'N/A')}")
        
        # Show first paper
        if result.get('papers'):
            paper = result['papers'][0]
            print(f"\n   Paper: {paper.get('title', 'N/A')}")
            print(f"   Score: {paper.get('score', 0):.2f}")
            if paper.get('meta'):
                authors = paper['meta'].get('authors', [])
                if authors:
                    print(f"   Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
        
        # Show first news
        if result.get('news'):
            news = result['news'][0]
            print(f"\n   News: {news.get('title', 'N/A')}")
            print(f"   Score: {news.get('score', 0):.2f}")
            if news.get('meta'):
                print(f"   Outlet: {news['meta'].get('outlet', 'N/A')}")
        
        # Show errors if any
        if result.get('errors'):
            print(f"\n5. Errors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"   - {error}")
        
        print("\n" + "=" * 80)
        print("\nTest completed successfully!")
        
        # Optionally save results to file
        # with open('hansen_lab_results.json', 'w') as f:
        #     json.dump(result, f, indent=2, default=str)
        # print("Results saved to hansen_lab_results.json")
        
        return result
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("URL Research Service Test")
    print("=" * 80)
    test_url_research()
