# AI Deployment Guide for FRED Category Collection

## Purpose
This guide is intended for AI assistants or developers who need to reproduce or deploy the FRED category collection system, either locally or on Azure.

## Key Concepts

### 1. FRED API Structure
- FRED uses a hierarchical category system to organize ~800,000 economic data series
- Categories can have parent-child relationships up to 5+ levels deep
- Leaf categories (no children) contain the actual data series
- Every series belongs to one or more categories

### 2. Collection Strategy
- Start from root category (ID: 0)
- Recursively traverse all children using breadth-first search
- Track processed categories to avoid duplicates
- Save checkpoints every 50 categories for resilience
- Adapt rate limiting dynamically based on API responses

### 3. Rate Limiting
- FRED API limit: 120 requests per minute per API key
- Script uses adaptive rate limiting:
  - Starts at 0.55s sleep between calls
  - Increases to 1.0s max when hitting limits
  - Decreases to 0.5s min when successful
  - Automatically adjusts based on 429 responses

## Local Deployment

### Prerequisites
```bash
pip install requests
```

### Running the Collection
```bash
python3 collect_categories_adaptive.py
```

### Configuration
- API_KEY: Your FRED API key (get from https://fred.stlouisfed.org/docs/api/api_key.html)
- OUTPUT_DIR: Where to save results (default: "fred_complete_data")
- Sleep times: Adjust MIN_SLEEP_TIME and MAX_SLEEP_TIME if needed

### Expected Outputs
1. `categories_complete_hierarchy.json` - Full category tree
2. `categories_leaf_only.json` - Just leaf categories for series discovery
3. `category_collection_adaptive.log` - Detailed logs
4. `category_collection_checkpoint.json` - Progress checkpoint (deleted on completion)

## Azure Deployment

### Option 1: Azure Functions
```python
import azure.functions as func
from collect_categories_adaptive import AdaptiveCategoryCollector

def main(req: func.HttpRequest) -> func.HttpResponse:
    collector = AdaptiveCategoryCollector()
    count = collector.collect_all_categories()
    return func.HttpResponse(f"Collected {count} categories")
```

### Option 2: Azure Container Instance
```dockerfile
FROM python:3.9-slim
COPY collect_categories_adaptive.py /app/
WORKDIR /app
RUN pip install requests
CMD ["python", "collect_categories_adaptive.py"]
```

### Option 3: Azure Batch
- Use for parallel collection of different endpoints
- Distribute leaf categories across compute nodes
- Aggregate results in Azure Storage

### Storing Results in Azure

#### Delta Lake Storage
```python
from delta import DeltaTable
import pandas as pd

# Convert JSON to DataFrame
df = pd.read_json('categories_complete_hierarchy.json')

# Write to Delta Lake
df.write.format("delta").mode("overwrite").save("abfss://container@storage.dfs.core.windows.net/fred/categories")
```

#### Cosmos DB Storage
```python
from azure.cosmos import CosmosClient

client = CosmosClient(url, key)
database = client.get_database_client("fred")
container = database.get_container_client("categories")

# Upload each category
for cat_id, cat_data in categories.items():
    container.upsert_item(cat_data)
```

## Monitoring and Maintenance

### Health Checks
- Monitor API call rate (should stay near 60/min)
- Check for rate limit hits (some are normal)
- Verify checkpoint saves every 50 categories
- Total collection time: ~5-6 hours

### Recovery from Failures
- Script automatically saves checkpoints
- To resume: just run the script again
- It will load the checkpoint and continue
- No duplicate work or API calls

### Scaling Considerations
- Cannot parallelize due to rate limits on single API key
- Consider multiple API keys for parallel collection
- Categories must be collected before series
- Series collection can be parallelized using leaf categories

## Next Steps After Collection

1. **Series Discovery**
   - Use leaf categories to find all series
   - Each leaf category contains multiple series
   - Use `/category/series` endpoint

2. **Series Metadata Collection**
   - Get details for each discovered series
   - Use batch endpoints where possible
   - Collect: units, frequency, sources, releases, tags

3. **Relationship Mapping**
   - Build series-to-category mappings
   - Create series-to-release mappings
   - Generate series-to-tag mappings

## Important Notes

- This collection is the foundation for complete FRED metadata extraction
- The hierarchical structure enables systematic discovery of all data
- Checkpointing ensures reliability over long collection periods
- Adaptive rate limiting maximizes throughput while respecting API limits
- The collected data serves as the index for all subsequent operations