"""Test both grants and papers agents via orchestrator."""
import sys
# Clear cached modules
for mod in list(sys.modules.keys()):
    if 'agents' in mod or 'models' in mod or 'orchestrator' in mod:
        del sys.modules[mod]

from models import ResearchState
from orchestrator import ORCHESTRATOR

# Run orchestrator with intent="all" to run both grants and papers agents
state = ResearchState(
    user_query="machine learning healthcare",
    intent="all"  # run all agents (grants, papers, news)
)

print("Running orchestrator with query: 'machine learning healthcare'")
print("Intent: all (grants + papers + news)")
print("-" * 60)

result = ORCHESTRATOR.invoke(state)

print(f"\n=== RESULTS ===")
print(f"Grants found: {len(result.get('grants', []))}")
print(f"Papers found: {len(result.get('papers', []))}")
print(f"News found: {len(result.get('news', []))}")
print(f"Total inbox cards: {len(result.get('inbox_cards', []))}")
print(f"Errors: {result.get('errors', [])}")

# Show top grants
print(f"\n=== TOP 3 GRANTS ===")
for i, g in enumerate(result.get('grants', [])[:3], 1):
    print(f"{i}. {g.title[:70]}...")
    print(f"   Score: {g.score:.2f} | Sponsor: {g.meta.get('sponsor', 'N/A')}")

# Show top papers
print(f"\n=== TOP 3 PAPERS ===")
for i, p in enumerate(result.get('papers', [])[:3], 1):
    print(f"{i}. {p.title[:70]}...")
    authors = p.meta.get('authors', [])[:2]
    author_str = ", ".join(authors) if authors else "N/A"
    print(f"   Score: {p.score:.2f} | Authors: {author_str}")

# Show top news
print(f"\n=== TOP 3 NEWS ===")
for i, n in enumerate(result.get('news', [])[:3], 1):
    print(f"{i}. {n.title[:70]}...")
    print(f"   Score: {n.score:.2f} | Outlet: {n.meta.get('outlet', 'N/A')}")
