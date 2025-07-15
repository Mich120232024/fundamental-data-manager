# FRED Complete Collection Method

## Overview

This document describes the comprehensive FRED metadata collection method that implements the exact Delta Lake schema approved by the research team. The method collects all 15 standard FRED series fields plus relationship mappings for categories, tags, and releases.

## Approved Schema Reference

The collection method implements the schema defined in:
`/Fred data collection/fred_production/core_analysis/fred_metadata_schema_analysis.md`

### Core Series Fields (15 standard fields)
1. **id** - Unique series identifier
2. **title** - Human-readable series name
3. **units** - Measurement units
4. **units_short** - Abbreviated units
5. **frequency** - Data frequency
6. **frequency_short** - Abbreviated frequency
7. **seasonal_adjustment** - SA method
8. **seasonal_adjustment_short** - Abbreviated SA
9. **observation_start** - First observation date
10. **observation_end** - Last observation date
11. **last_updated** - Last modification timestamp
12. **popularity** - Usage/popularity score
13. **realtime_start** - Real-time period start
14. **realtime_end** - Real-time period end
15. **notes** - Detailed description/methodology

### Delta Lake Tables
1. **fred_series** - Core metadata (partitioned by frequency)
2. **fred_series_categories** - Series-to-category mappings
3. **fred_series_tags** - Series-to-tag mappings
4. **fred_series_releases** - Series-to-release mappings

## Collection Architecture

### 1. Local Collection Script
**File**: `fred_approved_schema_collector.py`
- Implements FREDApprovedSchemaCollector class
- Handles rate limiting (0.6s between API calls)
- Collects all metadata and relationships
- Outputs Delta Lake-ready JSON files

### 2. Azure Synapse Ingestion
**File**: `synapse_notebooks/fred_delta_ingestion.py`
- Creates Delta Lake tables with exact schema
- Implements merge strategy for incremental updates
- Optimizes tables with Z-ordering
- Creates analysis views

### 3. Running the Collection

#### Quick Test (100 series)
```bash
cd "/Users/mikaeleage/Fred data collection"
python3 run_approved_collector.py
# Select option 1
```

#### Sample Collection (1,000 series)
```bash
python3 run_approved_collector.py
# Select option 2
```

#### Production Collection (10,000 series)
```bash
python3 run_approved_collector.py
# Select option 3
```

#### Full Collection (~730,000 series)
```bash
python3 run_approved_collector.py
# Select option 4
# Confirm with 'yes'
# Note: This will take 10-12 hours
```

## Output Structure

The collector creates the following files:
```
delta_lake_staging_[mode]/
├── fred_series.json              # Core metadata (newline-delimited JSON)
├── fred_series_categories.json   # Category mappings
├── fred_series_tags.json        # Tag mappings
├── fred_series_releases.json    # Release mappings
└── collection_metadata.json     # Collection statistics
```

## Azure Deployment Process

### 1. Upload to Azure Storage
```bash
# Using Azure CLI
az storage blob upload-batch \
  --account-name fredstorageaccount \
  --destination staging \
  --source delta_lake_staging_3/
```

### 2. Run Synapse Notebook
1. Open Azure Synapse Studio
2. Import `fred_delta_ingestion.py` notebook
3. Update storage account details
4. Run all cells
5. Verify data in Delta tables

### 3. Cosmos DB Deployment
Coordinate with Azure Infrastructure Agent using:
- Schema specification from this collection
- Partition strategies identified
- Index policies optimized for queries

## Collection Statistics (Expected)

Based on previous analysis:
- **Total Series**: ~730,000
- **Categories**: 5,183
- **Tags**: ~5,000 unique
- **Releases**: ~318 unique
- **API Calls Required**: ~800,000 (with relationships)
- **Estimated Time**: 10-12 hours for full collection

## Rate Limiting Strategy

- **Base Delay**: 0.6 seconds between calls
- **Retry Logic**: Exponential backoff on 429 errors
- **Batch Size**: 1,000 series per API call (FRED maximum)
- **Concurrent Requests**: None (sequential to respect rate limits)

## Data Quality Assurance

The collector includes:
1. **Field Validation**: Ensures all 15 fields present
2. **Relationship Integrity**: Tracks unique entities
3. **Error Handling**: Logs failed requests for retry
4. **Progress Tracking**: Real-time collection statistics
5. **Checkpointing**: Can resume from interruption

## Incremental Update Strategy

The Delta Lake merge strategy:
1. Uses `last_updated` timestamp for change detection
2. Updates changed series metadata
3. Adds new series without duplication
4. Preserves relationship mappings
5. Maintains partition optimization

## Next Steps

1. **Run Test Collection**: Verify connectivity and schema
2. **Deploy to Azure**: Upload and ingest sample data
3. **Validate Schema**: Confirm Delta Lake tables match specification
4. **Plan Full Collection**: Schedule 10-12 hour collection window
5. **Implement Updates**: Set up daily/weekly incremental updates

## Support Files

- `test_approved_collector.py` - Quick validation script
- `run_approved_collector.py` - Interactive collection runner
- `fred_delta_ingestion.py` - Synapse ingestion notebook
- `AZURE_COSMOS_DEPLOYMENT_SPEC.md` - Cosmos DB specifications

## Contact

For questions or issues:
- Review: `/Fred data collection/fred_production/core_analysis/`
- Check: Team agenda for latest updates
- Coordinate: With Azure Infrastructure Agent for deployment