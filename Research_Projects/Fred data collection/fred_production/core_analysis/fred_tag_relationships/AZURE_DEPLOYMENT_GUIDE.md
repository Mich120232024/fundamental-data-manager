# Azure Deployment Guide - FRED Tag Relationships

## Overview

This guide provides the COMPLETE method for deploying tag relationship collection to Azure. No sampling, no shortcuts - full production collection.

## Data Volume Estimates

Based on our analysis:
- **5,941 tags** to process
- **~30,000 API calls** required (avg 5 calls per tag due to pagination)
- **~16.4 million relationships** expected
- **2-3 GB** of JSON data
- **5-6 hours** collection time

## Azure Architecture

### 1. Delta Lake Table Schema

```sql
-- Primary relationship table
CREATE TABLE IF NOT EXISTS fred.tag_relationships (
    source_tag STRING NOT NULL,
    related_tag STRING NOT NULL,
    series_count INT,
    popularity INT,
    group_id STRING,
    notes STRING,
    created TIMESTAMP,
    collection_date DATE,
    batch_id STRING
) USING DELTA
PARTITIONED BY (group_id, collection_date)
LOCATION 'abfss://container@storage.dfs.core.windows.net/fred/tag_relationships'

-- Metadata tracking table
CREATE TABLE IF NOT EXISTS fred.tag_collection_metadata (
    tag_name STRING NOT NULL,
    total_relationships INT,
    api_calls_required INT,
    collection_status STRING,
    last_updated TIMESTAMP,
    error_message STRING
) USING DELTA
LOCATION 'abfss://container@storage.dfs.core.windows.net/fred/tag_metadata'
```

### 2. Azure Data Factory Pipeline

```json
{
  "name": "FRED_Tag_Relationships_Complete",
  "activities": [
    {
      "name": "LoadAllTags",
      "type": "Lookup",
      "dataset": "tags_complete_json"
    },
    {
      "name": "ForEachTag",
      "type": "ForEach",
      "items": "@activity('LoadAllTags').output.value",
      "isSequential": false,
      "batchCount": 10,
      "activities": [
        {
          "name": "CollectTagRelationships",
          "type": "AzureFunction",
          "functionName": "CollectFredTagRelationships",
          "body": {
            "tag_name": "@item().name",
            "limit": 1000,
            "use_pagination": true
          }
        }
      ]
    }
  ]
}
```

### 3. Azure Function for Collection

```python
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import json
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    tag_name = req.params.get('tag_name')
    
    # Collect with pagination
    all_relationships = []
    offset = 0
    
    while True:
        response = call_fred_api('/related_tags', {
            'tag_names': tag_name,
            'limit': 1000,
            'offset': offset
        })
        
        if not response or len(response['tags']) == 0:
            break
            
        all_relationships.extend(response['tags'])
        
        if len(response['tags']) < 1000:
            break
            
        offset += 1000
    
    # Write to Delta Lake
    write_to_delta_lake(tag_name, all_relationships)
    
    return func.HttpResponse(f"Collected {len(all_relationships)} relationships")
```

### 4. Monitoring and Checkpointing

```python
# Checkpoint table
CREATE TABLE fred.collection_checkpoint (
    tag_name STRING PRIMARY KEY,
    status STRING,
    relationships_collected INT,
    api_calls_made INT,
    last_offset INT,
    updated_at TIMESTAMP
) USING DELTA
```

## Deployment Steps

### Phase 1: Infrastructure Setup
1. Create Azure Storage Account with hierarchical namespace
2. Create Delta Lake containers
3. Deploy Azure Functions for API collection
4. Set up Azure Data Factory

### Phase 2: Initial Load
1. Load `tags_complete.json` to blob storage
2. Create checkpoint table
3. Start ADF pipeline with 10 parallel threads
4. Monitor progress via checkpoint table

### Phase 3: Incremental Updates
1. Daily: Check for new tags
2. Weekly: Refresh high-value tags (top 100 by series_count)
3. Monthly: Full refresh of all relationships

## Performance Optimization

1. **Parallel Processing**: 10 concurrent tag collections
2. **Batch Writing**: Write 1000 relationships at a time
3. **Compression**: Use Snappy compression for Delta files
4. **Caching**: Cache frequently accessed relationships

## Cost Estimates

- **API Calls**: 30,000 calls = ~$0 (free tier)
- **Storage**: 3GB compressed = ~$0.05/month
- **Compute**: 6 hours Azure Functions = ~$5
- **Total Initial Load**: ~$5-10

## Success Criteria

✅ All 5,941 tags processed
✅ Zero missing relationships
✅ Complete graph traversal capability
✅ Sub-second query performance
✅ Daily incremental updates working

---
*This is the production deployment guide for complete FRED tag relationship collection*