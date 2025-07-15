# FRED API User Guide - From Collection to Azure

## 🎯 Quick Start

### What You Have Now
1. **Complete Foundation Data** (100%)
   - 91 sources
   - 326 releases  
   - 8,000+ tags
   - 5,183 categories

2. **Validated Methods**
   - All 30 working endpoints tested
   - Pagination patterns proven
   - Rate limiting solved

3. **Sample Data**
   - 150 series with complete metadata
   - Tag relationship samples
   - All schemas verified

## 📋 Collection Roadmap

### Phase 1: Series Discovery (Already Started)
```bash
# We have categories, now get all series
python collect_all_series_from_categories.py
# Expected: ~800,000 series IDs
# Time: 7 hours with 10 workers
```

### Phase 2: Series Metadata
```bash
# For each series, collect 4 endpoints
python collect_series_metadata.py
# Endpoints: /series, /series/categories, /series/tags, /series/release
# Time: 45 hours with 10 workers
```

### Phase 3: Tag Relationships
```bash
# Complete tag graph
python collect_all_tag_relationships_production.py
# Expected: 16.4M relationships
# Time: 5-6 hours
```

### Phase 4: Remaining Relationships
```bash
# Category relationships, release mappings, etc.
python collect_remaining_relationships.py
# Time: 2-3 hours
```

## 🗄️ Azure Delta Lake Schema

### Core Tables
```sql
-- 1. Series Master Table
CREATE TABLE fred.series (
    id STRING PRIMARY KEY,
    title STRING,
    units STRING,
    frequency STRING,
    seasonal_adjustment STRING,
    observation_start DATE,
    observation_end DATE,
    last_updated TIMESTAMP,
    -- ... other fields
) USING DELTA
PARTITIONED BY (frequency)

-- 2. Relationships
CREATE TABLE fred.series_categories (
    series_id STRING,
    category_id INT,
    PRIMARY KEY (series_id, category_id)
) USING DELTA

CREATE TABLE fred.series_tags (
    series_id STRING,
    tag_name STRING,
    PRIMARY KEY (series_id, tag_name)
) USING DELTA

CREATE TABLE fred.tag_relationships (
    source_tag STRING,
    related_tag STRING,
    series_count INT,
    PRIMARY KEY (source_tag, related_tag)
) USING DELTA
PARTITIONED BY (source_tag)
```

## 🚀 Azure Deployment Steps

### 1. Infrastructure Setup
```bash
# Create storage account
az storage account create \
  --name fredstorage \
  --resource-group fred-rg \
  --location eastus \
  --sku Standard_LRS \
  --enable-hierarchical-namespace true

# Create containers
az storage container create \
  --account-name fredstorage \
  --name fred-metadata
```

### 2. Deploy Collection Functions
```python
# Azure Function for API collection
@app.function_name(name="FredCollector")
@app.schedule(schedule="0 */6 * * *")  # Every 6 hours
def fred_collector(timer: func.TimerRequest):
    # Check for updates
    updates = check_fred_updates()
    if updates:
        collect_incremental_data(updates)
```

### 3. Data Factory Pipeline
```json
{
  "pipeline": {
    "name": "FRED_Complete_Collection",
    "activities": [
      {
        "name": "DiscoverSeries",
        "type": "Custom",
        "typeProperties": {
          "command": "python discover_all_series.py"
        }
      },
      {
        "name": "CollectMetadata",
        "type": "ForEach",
        "items": "@activity('DiscoverSeries').output",
        "batchCount": 10
      }
    ]
  }
}
```

## 📊 Query Examples

### Find Economic Indicators
```sql
-- GDP-related series
SELECT s.* 
FROM fred.series s
JOIN fred.series_tags st ON s.id = st.series_id
WHERE st.tag_name = 'gdp'
  AND s.frequency = 'Quarterly'
  AND s.seasonal_adjustment = 'Seasonally Adjusted'
```

### Explore Tag Relationships
```sql
-- What tags connect to inflation?
SELECT related_tag, series_count
FROM fred.tag_relationships
WHERE source_tag = 'inflation'
ORDER BY series_count DESC
LIMIT 20
```

### Category Navigation
```sql
-- All series in housing category
SELECT s.*
FROM fred.series s
JOIN fred.series_categories sc ON s.id = sc.series_id
WHERE sc.category_id = 32991  -- Housing category
```

## 🔧 Maintenance

### Daily Updates
```python
# Check for updated series
updates = api_call('/series/updates', {
    'filter_value': 'all',
    'start_time': yesterday
})

# Update only changed series
for series_id in updates:
    refresh_series_metadata(series_id)
```

### Weekly Validation
```python
# Verify data completeness
missing = find_missing_relationships()
if missing:
    collect_missing_data(missing)
```

## 📈 Success Metrics

✅ **Complete Collection**
- [ ] 800,000+ series discovered
- [ ] All series metadata collected
- [ ] All relationships mapped
- [ ] Tag graph complete

✅ **Performance**
- [ ] Query response < 1 second
- [ ] Daily updates < 1 hour
- [ ] 99.9% data availability

✅ **Quality**
- [ ] No missing relationships
- [ ] All schemas validated
- [ ] Referential integrity maintained

---

## Need Help?

1. **API Issues**: Check rate limits, use adaptive delays
2. **Storage Issues**: Verify Delta Lake partitioning
3. **Query Performance**: Add Z-ordering on common filters
4. **Updates Failing**: Check checkpoint files

Remember: We're collecting EVERYTHING, no sampling!