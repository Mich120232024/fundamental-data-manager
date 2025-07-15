# Quick Cosmos DB Access Guide

## 1. Web Viewer (Recommended)
```bash
# Start the web server
cd "/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts"
python3 cosmos_viewer_server.py
```
Then open: http://localhost:5001/viewer

## 2. Command Line Access
```bash
# Check your messages
cd "/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts"
python3 check_agent_messages.py

# Search for specific content
python3 search_cosmos.py "keyword"

# Get SAM's latest messages
python3 -c "from cosmos_db_manager import get_db_manager; db = get_db_manager(); msgs = db.get_agent_inbox('SAM'); print(f'SAM has {len(msgs)} messages'); [print(f'{m["subject"]}') for m in msgs[:5]]"
```

## 3. Python Interactive
```python
# Start Python in the scripts directory
cd "/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts"
python3

# Then run:
from cosmos_db_manager import get_db_manager
db = get_db_manager()

# Check your inbox
messages = db.get_agent_inbox('mikaeleage')
for msg in messages[:5]:
    print(f"From: {msg.get('from', 'Unknown')}")
    print(f"Subject: {msg.get('subject', 'No subject')}")
    print(f"Time: {msg.get('timestamp', 'No timestamp')}")
    print("-" * 50)

# Search across all containers
results = db.search_messages("enriched policy")
print(f"Found {len(results)} results")
```

## 4. Quick Status Check
```bash
# One-liner to see database stats
python3 -c "from cosmos_db_manager import get_db_manager; db = get_db_manager(); print(f'Connected to: {db.database_name}'); containers = list(db.database.list_containers()); print(f'Containers: {len(containers)}'); print('Top containers:', [c['id'] for c in containers[:5]])"
```

## Available Containers
- **messages**: Agent communications (736+ docs)
- **audit**: Governance tracking (55+ docs)
- **documents**: Migrated docs (41+ docs)
- **logs**: System logs (29+ docs)
- **enforcement**: Compliance (24+ docs)
- **metadata**: System metadata (15+ docs)
- **processes**: Process docs (3+ docs)

## Tips
- The web viewer auto-refreshes container counts
- Click any container to browse documents
- Click any document to see full JSON
- Use search to find content across containers
- Messages are partitioned by YYYY-MM for performance