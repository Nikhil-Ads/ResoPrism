"""Test grants agent via orchestrator."""
import sys
# Clear cached modules
for mod in list(sys.modules.keys()):
    if 'agents' in mod or 'models' in mod or 'orchestrator' in mod:
        del sys.modules[mod]

from models import ResearchState
from orchestrator import ORCHESTRATOR

# Run orchestrator with intent="grants" to only run grants agent
state = ResearchState(
    user_query="healthcare",  # keyword passed from orchestrator
    intent="grants"  # only run grants agent
)

result = ORCHESTRATOR.invoke(state)

print('=== ORCHESTRATOR -> GRANTS AGENT OUTPUT ===')
print(f'Intent: {result.get("intent")}')
print(f'Total grants found: {len(result.get("grants", []))}')
print(f'Inbox cards: {len(result.get("inbox_cards", []))}')
print(f'Errors: {result.get("errors", [])}')
print()

for i, g in enumerate(result.get("inbox_cards", [])[:5], 1):
    print(f'{i}. {g.title}')
    print(f'   Score: {g.score:.2f} | Badge: {g.badge}')
    print(f'   Sponsor: {g.meta.get("sponsor", "N/A")} | Close: {g.meta.get("close_date", "N/A")}')
    print()
