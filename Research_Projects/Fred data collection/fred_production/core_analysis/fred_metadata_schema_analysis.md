# FRED Metadata Schema Analysis

Based on the 150 series sample collection completed on 2025-06-01

## Collection Summary
- **Series Collected**: 150
- **Categories Used**: 32 diverse categories
- **API Calls**: 182
- **Category Depths**: Depth 2 (95 series) and Depth 3 (55 series)

## Core Metadata Fields

Every FRED series contains these 15 standard fields:

1. **id** - Unique series identifier (e.g., "GDP", "UNRATE")
2. **title** - Human-readable series name
3. **units** - Measurement units (31 unique types found)
4. **units_short** - Abbreviated units
5. **frequency** - Data frequency (10 unique types found)
6. **frequency_short** - Abbreviated frequency
7. **seasonal_adjustment** - SA method (SA/NSA/SAAR)
8. **seasonal_adjustment_short** - Abbreviated SA
9. **observation_start** - First observation date
10. **observation_end** - Last observation date
11. **last_updated** - Last modification timestamp
12. **popularity** - Usage/popularity score
13. **realtime_start** - Real-time period start
14. **realtime_end** - Real-time period end
15. **notes** - Detailed description/methodology

## Data Types Summary

### Frequencies (10 types)
- Annual
- Quarterly (with variants)
- Monthly
- Weekly (multiple end days)
- Daily (with 7-day variant)
- 10 Year

### Units (31 types)
- Monetary: Dollars, Billions of Dollars, Dollars per Hour
- Indices: Various base years (2005, 2009, 2012, 2015, 2017)
- Percentages: Percent, Percent Change
- Quantities: Number, Thousands, Millions, Billions
- Physical: Barrels per Day, Metric Tons, Hours
- Binary: +1 or 0

### Seasonal Adjustments (3 types)
- Not Seasonally Adjusted (NSA)
- Seasonally Adjusted (SA)
- Seasonally Adjusted Annual Rate (SAAR)

## Delta Lake Table Design Recommendations

### 1. Core Series Table
```sql
CREATE TABLE fred_series (
    id STRING NOT NULL,                    -- Primary key
    title STRING,
    units STRING,
    units_short STRING,
    frequency STRING,
    frequency_short STRING,
    seasonal_adjustment STRING,
    seasonal_adjustment_short STRING,
    observation_start DATE,
    observation_end DATE,
    last_updated TIMESTAMP,
    popularity INT,
    realtime_start DATE,
    realtime_end DATE,
    notes STRING,                          -- Can be very long
    collection_timestamp TIMESTAMP,        -- When we collected this
    PRIMARY KEY (id)
) USING DELTA
PARTITIONED BY (frequency)                 -- Partition by frequency for query optimization
```

### 2. Series-Category Mapping Table
```sql
CREATE TABLE fred_series_categories (
    series_id STRING NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (series_id, category_id)
) USING DELTA
```

### 3. Series-Tags Mapping Table
```sql
CREATE TABLE fred_series_tags (
    series_id STRING NOT NULL,
    tag_name STRING NOT NULL,
    group_id STRING,
    PRIMARY KEY (series_id, tag_name)
) USING DELTA
```

### 4. Series-Release Mapping Table
```sql
CREATE TABLE fred_series_releases (
    series_id STRING NOT NULL,
    release_id INT NOT NULL,
    PRIMARY KEY (series_id, release_id)
) USING DELTA
```

## Key Insights

1. **Standardized Structure**: All series share exactly the same 15 fields
2. **Many-to-Many Relationships**: Series can belong to multiple categories, tags, and releases
3. **Temporal Data**: Multiple date fields for tracking real-time updates
4. **Text Heavy**: Notes field can contain extensive documentation
5. **Popularity Metric**: Built-in usage tracking for prioritization

## Next Steps

1. **Schema Validation**: Test Delta Lake tables with sample data
2. **Indexing Strategy**: Create indexes on frequently queried fields (frequency, units, dates)
3. **Partitioning**: Consider partitioning by frequency or last_updated for performance
4. **Data Quality**: Implement validation rules for dates, units, and relationships
5. **Update Strategy**: Design incremental update process using last_updated timestamp