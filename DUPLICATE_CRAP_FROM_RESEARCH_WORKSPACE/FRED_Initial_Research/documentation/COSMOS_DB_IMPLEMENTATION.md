# FRED API Catalog - Cosmos DB Implementation

## Overview

This document describes the Cosmos DB implementation for the FRED API catalog, providing a high-performance, scalable document database optimized for hierarchical data and analytical workloads.

## Architecture Design

### Multi-Container Strategy

**3-Container Architecture** for optimal performance and cost efficiency:

1. **`fred-catalog`** - Main metadata repository
2. **`fred-observations`** - Time series data with high volume capacity  
3. **`fred-updates`** - Change tracking with auto-cleanup

### Container Specifications

#### 1. fred-catalog Container

**Purpose**: Categories, Series, Sources, Releases, and Tags metadata

```json
{
  "partition_key": "/pk",
  "throughput": "1,000-10,000 RU/s (autoscale)",
  "estimated_size": "~1GB at full scale",
  "document_count": "~840,000 documents",
  "cost_estimate": "$80-800/month"
}
```

**Optimized Indexing Policy**:
- **Included**: `/pk`, `/type`, `/parent_id`, `/depth`, `/name`, `/category/id`, `/metadata/frequency`, `/popularity`
- **Excluded**: `/children/*`, `/ancestors/*`, `/metadata/notes`, `/collection_metadata/*`
- **Composite Indexes**: 4 optimized combinations for common query patterns

#### 2. fred-observations Container

**Purpose**: Historical economic time series data

```json
{
  "partition_key": "/series_id", 
  "throughput": "4,000-40,000 RU/s (autoscale)",
  "estimated_size": "2-5TB potential",
  "document_count": "~100M observations",
  "cost_estimate": "$320-3200/month"
}
```

**Time Series Optimized Indexing**:
- **Included**: `/series_id`, `/date`, `/value`, `/realtime_start`, `/realtime_end`
- **Composite Indexes**: Optimized for time range queries and real-time data access

#### 3. fred-updates Container

**Purpose**: Change tracking and audit trail

```json
{
  "partition_key": "/date",
  "throughput": "400 RU/s (manual)",
  "ttl": "90 days auto-cleanup",
  "estimated_size": "<100MB annually",
  "cost_estimate": "$32/month"
}
```

## Schema Design

### Document Types

#### Category Document Schema
```json
{
  "id": "32073",
  "pk": "32073",
  "name": "Population, Employment, & Labor Markets",
  "parent_id": "32263",
  "depth": 2,
  "full_path": ["U.S. Regional Data", "Population, Employment, & Labor Markets"],
  "path_ids": ["32263", "32073"],
  "children": [{"id": "32445", "name": "States"}],
  "ancestors": [{"id": "32263", "name": "U.S. Regional Data", "depth": 1}],
  "descendants_count": 847,
  "series_count": 124,
  "last_updated": "2025-06-26T10:00:00Z",
  "type": "category"
}
```

**Key Features**:
- **Denormalized hierarchy** for efficient traversal
- **Aggregated counts** for dashboard queries
- **Full path storage** eliminates recursive lookups

#### Series Document Schema
```json
{
  "id": "GDP",
  "pk": "GDP",
  "title": "Gross Domestic Product",
  "category": {
    "id": "18",
    "name": "National Accounts",
    "full_path": ["National Accounts"]
  },
  "metadata": {
    "frequency": "Quarterly",
    "frequency_short": "Q",
    "units": "Billions of Dollars",
    "observation_start": "1947-01-01",
    "observation_end": "2024-12-31",
    "last_updated": "2025-06-26T08:30:00Z"
  },
  "relationships": {
    "source_id": 1,
    "source_name": "Board of Governors of the Federal Reserve System",
    "release_id": 53,
    "release_name": "Gross Domestic Product",
    "tags": [
      {"name": "gdp", "group": "concept"},
      {"name": "quarterly", "group": "frequency"}
    ]
  },
  "popularity": 100,
  "type": "series"
}
```

**Key Features**:
- **Embedded category info** reduces join operations
- **Denormalized relationships** for performance
- **Popularity scoring** for relevance ranking

## Partition Key Strategy

### High-Cardinality Distribution

**All containers use ID-based partitioning**:
- **Categories**: 5,183 unique partition keys
- **Series**: 830,000+ unique partition keys  
- **Updates**: Date-based partitioning for time-series access

**Benefits**:
- Even distribution prevents hot partitions
- Excellent scalability to millions of documents
- Optimal for point lookups by ID
- Supports efficient cross-partition queries

## Query Optimization Patterns

### Common Query Examples

#### Hierarchy Traversal
```sql
-- Get all children of a category (single partition)
SELECT * FROM c 
WHERE c.parent_id = @categoryId 
AND c.type = 'category'

-- Get category path (denormalized, single lookup)
SELECT c.full_path, c.ancestors 
FROM c 
WHERE c.id = @categoryId 
AND c.type = 'category'
```

#### Series Discovery
```sql
-- Find series by category (uses composite index)
SELECT * FROM c 
WHERE c.category.id = @categoryId 
AND c.type = 'series'
ORDER BY c.popularity DESC

-- Recent updates (composite index optimization)
SELECT * FROM c 
WHERE c.metadata.last_updated > @timestamp 
AND c.type = 'series'
ORDER BY c.metadata.last_updated DESC
```

#### Analytics Queries
```sql
-- Series by frequency and popularity
SELECT * FROM c 
WHERE c.metadata.frequency = 'Quarterly'
AND c.type = 'series'
ORDER BY c.popularity DESC

-- Source-based analysis
SELECT * FROM c 
WHERE c.relationships.source_id = @sourceId
AND c.type = 'series'
```

## Cost Optimization

### Estimated Monthly Costs

| Environment | Catalog | Observations | Updates | Total |
|-------------|---------|--------------|---------|-------|
| Development | $80 | $320 | $32 | $432 |
| Production (initial) | $400 | $1,600 | $32 | $2,032 |
| Production (full scale) | $800 | $3,200 | $32 | $4,032 |

### Cost Reduction Strategies

1. **Reserved Capacity**: 30% savings on consistent workloads
2. **Selective Indexing**: Exclude large text fields from indexing
3. **Document Size Optimization**: Abbreviate field names in nested objects
4. **TTL Management**: Auto-cleanup for transient data
5. **Analytical Store**: Cost-effective analytics on historical data

## Performance Characteristics

### Read Performance
- **Point Lookups**: 2-5ms latency (single partition)
- **Category Traversal**: 5-10ms (denormalized hierarchy)
- **Cross-partition Queries**: 50-200ms (depending on fanout)
- **Analytical Queries**: 100-500ms (with proper indexing)

### Write Performance
- **Single Document**: 5-10ms
- **Batch Operations**: 50-100 docs/sec per partition
- **Bulk Load**: 10,000+ docs/sec (distributed across partitions)

### Scalability Limits
- **Storage**: Unlimited (20GB per partition)
- **Throughput**: 10,000 RU/s per partition
- **Documents**: Unlimited
- **Query Complexity**: Limited by 5-second timeout

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [x] Container design and schema optimization
- [x] Indexing policy implementation  
- [x] Sample data validation
- [ ] Foundation data upload from FRED JSON files

### Phase 2: Data Loading (Week 2)
- [ ] Categories bulk import (5,183 documents)
- [ ] Series metadata import (initial batch)
- [ ] Sources and releases import
- [ ] Tags relationship mapping

### Phase 3: Query Optimization (Week 3)
- [ ] Performance testing and tuning
- [ ] Index optimization based on usage patterns
- [ ] Change feed implementation
- [ ] Monitoring and alerting setup

### Phase 4: Production Readiness (Week 4)
- [ ] Multi-region replication
- [ ] Backup and disaster recovery
- [ ] Reserved capacity optimization
- [ ] Analytical store enablement

## Deployment Commands

### 1. Create Database and Containers
```bash
cd /Users/mikaeleage/Research\ \&\ Analytics\ Services/Projects/FRED_Initial_Research/deployment

python create_cosmos_database.py \
  --cosmos-url "https://your-cosmos-account.documents.azure.com:443/" \
  --cosmos-key "your-cosmos-key" \
  --database-name "fred-data" \
  --validate \
  --test-data
```

### 2. Load Foundation Data
```bash
python load_foundation_data.py \
  --cosmos-url "https://your-cosmos-account.documents.azure.com:443/" \
  --cosmos-key "your-cosmos-key" \
  --data-dir "../data"
```

### 3. Validate Performance
```bash
python validate_performance.py \
  --cosmos-url "https://your-cosmos-account.documents.azure.com:443/" \
  --cosmos-key "your-cosmos-key" \
  --run-benchmarks
```

## Monitoring and Maintenance

### Key Metrics to Monitor
- **RU Consumption**: Stay within autoscale limits
- **Query Latency**: <100ms for catalog queries
- **Document Size**: <2MB per document
- **Index Usage**: Optimize based on query patterns
- **Cost Tracking**: Monitor against budget thresholds

### Maintenance Tasks
- **Weekly**: Review RU consumption and adjust autoscale
- **Monthly**: Analyze query patterns and optimize indexes  
- **Quarterly**: Evaluate reserved capacity opportunities
- **Annually**: Review partitioning strategy for scale

## Integration Points

### With Delta Lake (Azure Synapse)
- **Change Feed**: Real-time sync to Delta tables
- **Analytical Store**: Direct analytics without ETL
- **Query Federation**: Join Cosmos + Delta data

### With Azure Functions
- **Triggers**: Change feed triggers for processing
- **Bindings**: Direct document operations
- **Scaling**: Consumption plan cost optimization

### With Application Services
- **Connection String**: Secure Key Vault integration
- **SDKs**: .NET, Python, JavaScript native support
- **Caching**: Azure Redis Cache for hot data

## Next Steps

1. **Deploy Infrastructure**: Run create_cosmos_database.py with production credentials
2. **Load Foundation Data**: Import the 5,183 categories and metadata
3. **Implement Change Feed**: Set up real-time sync to Delta Lake
4. **Performance Testing**: Validate query patterns and optimize
5. **Production Monitoring**: Set up comprehensive observability

This implementation provides a robust, scalable foundation for the FRED API catalog with optimized performance and cost characteristics suitable for both development and production workloads.