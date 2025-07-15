# Azure Cosmos DB Deployment Specification for FRED Data

**Generated**: 2025-06-26  
**Data Source**: Live FRED API Analysis  
**Purpose**: Optimal Cosmos DB schema for economic data platform

## 🎯 **Database Design Overview**

### **Database Configuration**
- **Name**: `fred_economic_data`
- **Consistency Level**: `Session` (optimal for read-heavy workloads)
- **Shared Throughput**: 1000 RU/s (cost-optimized)
- **Backup**: Periodic (4-hour intervals, 30-day retention)

## 🗃️ **Container Architecture**

### **1. Sources Container**
```json
{
  "name": "sources",
  "partition_key": "/id",
  "estimated_size": 117,
  "entity_type": "Data providers (Fed, BLS, etc.)",
  "indexing": ["name", "link"],
  "unique_key": "/id"
}
```
**Sample Document**:
```json
{
  "id": 1,
  "name": "Board of Governors of the Federal Reserve System (US)",
  "link": "http://www.federalreserve.gov/",
  "realtime_start": "2025-06-01",
  "realtime_end": "2025-06-01"
}
```

### **2. Releases Container**
```json
{
  "name": "releases",
  "partition_key": "/id", 
  "estimated_size": 318,
  "entity_type": "Data publications and reports",
  "indexing": ["name", "realtime_start", "realtime_end"],
  "unique_key": "/id"
}
```

### **3. Categories Container** 🌳
```json
{
  "name": "categories",
  "partition_key": "/parent_id",
  "estimated_size": 708,
  "entity_type": "Hierarchical data organization",
  "indexing": ["name", "parent_id", "depth"],
  "unique_key": "/id"
}
```
**Sample Document**:
```json
{
  "id": 32991,
  "name": "Money, Banking, & Finance",
  "parent_id": 0,
  "depth": 1
}
```

### **4. Tags Container** 🏷️
```json
{
  "name": "tags",
  "partition_key": "/group_id",
  "estimated_size": 1000,
  "entity_type": "Series classification system",
  "indexing": ["name", "group_id", "popularity", "series_count"]
}
```

### **5. Series Container** 📈
```json
{
  "name": "series",
  "partition_key": "/source_category_id",
  "estimated_size": 40000,
  "entity_type": "Economic time series metadata",
  "indexing": ["title", "units", "frequency", "source_category_id"],
  "unique_key": "/id"
}
```
**Sample Document**:
```json
{
  "id": "GDP",
  "title": "Gross Domestic Product",
  "units": "Billions of Dollars",
  "frequency": "Quarterly",
  "source_category_id": 106,
  "observation_start": "1947-01-01",
  "observation_end": "2025-01-01"
}
```

### **6. Relationships Container** 🔗
```json
{
  "name": "relationships",
  "partition_key": "/relationship_type",
  "estimated_size": 765,
  "entity_type": "Entity relationships and links",
  "indexing": ["from_entity", "to_entity", "relationship_type"]
}
```

## 🚀 **Azure CLI Deployment Commands**

### **Phase 1: Container Creation**
```bash
# Set environment variables
export COSMOS_ACCOUNT="your-cosmos-account-name"
export RESOURCE_GROUP="your-resource-group"

# Create database
az cosmosdb sql database create \
  --account-name $COSMOS_ACCOUNT \
  --name fred_economic_data \
  --throughput 1000

# Create containers
az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name fred_economic_data \
  --name sources \
  --partition-key-path "/id" \
  --throughput 400

az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name fred_economic_data \
  --name releases \
  --partition-key-path "/id" \
  --throughput 400

az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name fred_economic_data \
  --name categories \
  --partition-key-path "/parent_id" \
  --throughput 400

az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name fred_economic_data \
  --name tags \
  --partition-key-path "/group_id" \
  --throughput 400

az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name fred_economic_data \
  --name series \
  --partition-key-path "/source_category_id" \
  --throughput 400

az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name fred_economic_data \
  --name relationships \
  --partition-key-path "/relationship_type" \
  --throughput 400
```

## 📊 **Query Patterns & Optimization**

### **Common Query Patterns**
```sql
-- Find all series in a category
SELECT * FROM series s WHERE s.source_category_id = 125

-- Get category hierarchy
SELECT * FROM categories c WHERE c.parent_id = 32991

-- Search series by tag
SELECT s.* FROM series s 
JOIN relationships r ON s.id = r.series_id 
WHERE r.relationship_type = "series_tag" AND r.tag_name = "gdp"

-- Get all sources
SELECT * FROM sources ORDER BY s.name
```

### **Index Optimization**
- **Composite indexes** on frequently queried combinations
- **Exclude large text fields** (notes) from indexing
- **Range indexes** on date fields for time-based queries

## 📈 **Data Migration Strategy**

### **Phase 1: Foundation Data** (30 minutes)
1. ✅ Create Cosmos DB containers
2. ✅ Configure indexing policies  
3. ✅ Set up monitoring

### **Phase 2: Data Upload** (2 hours)
1. **Sources**: 117 records → Cosmos
2. **Releases**: 318 records → Cosmos
3. **Categories**: 708 records → Cosmos (with hierarchy)
4. **Tags**: 1000 records → Cosmos
5. **Series Metadata**: 40k+ records → Cosmos
6. **Relationships**: 765+ relationship documents

### **Phase 3: Production Optimization** (Ongoing)
1. Monitor query performance
2. Adjust RU/s based on usage
3. Optimize indexes based on real queries
4. Implement change feed for real-time updates

## 💰 **Cost Estimation**

### **Initial Setup**
- **Shared Throughput**: 1000 RU/s = ~$58/month
- **Storage**: ~10GB estimated = ~$2.50/month
- **Total Estimated**: ~$60/month initially

### **Production Scale**
- **With full series data**: ~40k series
- **Estimated storage**: ~50GB 
- **Throughput needs**: 2000-5000 RU/s
- **Production cost**: ~$150-300/month

## 🔍 **Next Steps for Azure Infrastructure Agent**

1. **✅ Use provided Azure CLI commands** to create containers
2. **✅ Deploy with exact partition key strategies** specified
3. **✅ Configure indexing policies** as documented
4. **✅ Set up monitoring** for query performance
5. **✅ Prepare for data migration** from our collected files

## 📁 **Available Data Files**

Ready for upload to Cosmos DB:
- `sources_raw.json` (117 sources)
- `releases_raw.json` (318 releases) 
- `category_hierarchy.json` (708 categories)
- `tags_raw.json` (1000 tags)
- `series_sample.json` (57 sample series)

**Location**: `/Users/mikaeleage/Fred data collection/schema_analysis_output/`

---

**This schema is optimized for**:
- ✅ Hierarchical category queries
- ✅ Series discovery by category/tag
- ✅ Economic data relationships
- ✅ Cost-effective partitioning
- ✅ Fast metadata searches

**Ready for Azure deployment!**

—DATA_ANALYST