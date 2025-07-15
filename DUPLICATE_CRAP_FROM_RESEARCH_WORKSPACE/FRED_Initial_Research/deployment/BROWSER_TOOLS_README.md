# API Registry Browser Tools

## Quick Browser Tools Created

### 1. **view_api_registry.py** - One-time View
Quick overview of the container contents:
```bash
poetry run python Projects/FRED_Initial_Research/deployment/view_api_registry.py
```

Shows:
- Container statistics (document counts by category)
- System documents (schema requirements, validation rules)
- API documents in table format
- Container configuration details

### 2. **quick_api_browser.py** - Interactive Browser
Simple interactive browser for exploring the registry:
```bash
poetry run python Projects/FRED_Initial_Research/deployment/quick_api_browser.py
```

Features:
- View all APIs
- Filter by category
- View schema requirements
- Search by name
- Container statistics

### 3. **api_registry_browser.py** - Full-Featured Browser
Advanced browser with export capabilities (requires tabulate):
```bash
# Install tabulate first
poetry add tabulate

# Run browser
poetry run python Projects/FRED_Initial_Research/deployment/api_registry_browser.py
```

Features:
- Table view of all documents
- Advanced filtering (category, status, auth type, protocol)
- Search functionality
- Export to JSON/CSV
- Detailed document viewer
- Statistics dashboard

## Current Container Status

**Total Documents**: 5
- System documents: 2
  - `schema_requirements_v1` - Defines what each field requires
  - `validation_rules_v1` - Allowed values and validation rules
- Test APIs: 3 (can be cleaned up)

**Container Configuration**:
- Partition Key: `/category`
- Indexing: Optimized for table queries
- Serverless: Pay-per-request pricing

## Usage Examples

### View All APIs:
```python
query = "SELECT * FROM c WHERE c.category != 'system' ORDER BY c.apiName"
```

### View Schema Requirements:
```python
schema = container.read_item(
    item="schema_requirements_v1",
    partition_key="system"
)
```

### Filter by Category:
```python
query = "SELECT * FROM c WHERE c.category = 'financial'"
```

### Search APIs:
```python
query = """
SELECT * FROM c 
WHERE CONTAINS(LOWER(c.apiName), LOWER('weather'))
   OR CONTAINS(LOWER(c.provider), LOWER('weather'))
"""
```

## Next Steps

1. Clean up test APIs if needed
2. Load the 500 production APIs from catalog
3. Use browser tools to verify data
4. Query through your interface using table structure