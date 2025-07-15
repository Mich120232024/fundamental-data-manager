# Databricks notebook source
# FRED Delta Lake Test Notebook - Best Practices Implementation
# Purpose: Test and validate Delta Lake formats, partitioning, and optimization for FRED data
# Platform: Azure Synapse Analytics
# Author: FRED Data Collection Team
# Version: 1.0

# COMMAND ----------

# MAGIC %md
# MAGIC # FRED Delta Lake Best Practices Test Notebook
# MAGIC 
# MAGIC ## Objectives:
# MAGIC 1. Test optimal Delta Lake table structures for FRED data
# MAGIC 2. Validate partitioning strategies
# MAGIC 3. Test Z-ordering and optimization
# MAGIC 4. Benchmark query performance
# MAGIC 5. Establish best practices for production

# COMMAND ----------

# IMPORTS AND CONFIGURATION
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import DeltaTable
import json
import time
from datetime import datetime, timedelta

# Storage Configuration - UPDATE WITH YOUR STORAGE ACCOUNT
STORAGE_ACCOUNT = "fredstorageaccount"  # Replace with actual storage account
CONTAINER = "fred-delta-lake"
STORAGE_PATH = f"abfss://{CONTAINER}@{STORAGE_ACCOUNT}.dfs.core.windows.net"

# Delta Lake Paths
TEST_PATH = f"{STORAGE_PATH}/test"
BRONZE_PATH = f"{STORAGE_PATH}/bronze"
SILVER_PATH = f"{STORAGE_PATH}/silver"
GOLD_PATH = f"{STORAGE_PATH}/gold"

print(f"Storage configured: {STORAGE_PATH}")
print(f"Test environment ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Delta Lake Schema Design for FRED

# COMMAND ----------

# FRED Series Metadata Schema (Optimized)
series_metadata_schema = StructType([
    # Primary identifiers
    StructField("series_id", StringType(), False),  # Primary key
    StructField("title", StringType(), True),
    StructField("observation_start", DateType(), True),
    StructField("observation_end", DateType(), True),
    
    # Categorization (for partitioning)
    StructField("frequency", StringType(), True),  # A, Q, M, W, D
    StructField("seasonal_adjustment", StringType(), True),
    StructField("units", StringType(), True),
    
    # Metadata
    StructField("last_updated", TimestampType(), True),
    StructField("popularity", IntegerType(), True),
    StructField("notes", StringType(), True),
    
    # Relationships
    StructField("category_id", IntegerType(), True),
    StructField("release_id", IntegerType(), True),
    StructField("source_id", IntegerType(), True),
    
    # Processing metadata
    StructField("collection_timestamp", TimestampType(), False),
    StructField("data_version", IntegerType(), False)
])

# FRED Observations Schema (Optimized for time series)
observations_schema = StructType([
    StructField("series_id", StringType(), False),
    StructField("date", DateType(), False),
    StructField("value", DoubleType(), True),
    StructField("realtime_start", DateType(), True),
    StructField("realtime_end", DateType(), True),
    StructField("collection_timestamp", TimestampType(), False)
])

# Categories Hierarchy Schema
categories_schema = StructType([
    StructField("category_id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("parent_id", IntegerType(), True),
    StructField("depth", IntegerType(), True),
    StructField("child_ids", ArrayType(IntegerType()), True),
    StructField("is_leaf", BooleanType(), True),
    StructField("series_count", IntegerType(), True)
])

print("✅ Schemas defined with proper data types")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create Test Delta Tables with Best Practices

# COMMAND ----------

def create_delta_table_with_properties(df, path, table_name, partition_cols=None, z_order_cols=None):
    """Create Delta table with best practices"""
    
    writer = df.write.format("delta").mode("overwrite")
    
    # Add partitioning if specified
    if partition_cols:
        writer = writer.partitionBy(*partition_cols)
    
    # Set Delta properties for optimization
    writer = writer.option("delta.autoOptimize.optimizeWrite", "true") \
                   .option("delta.autoOptimize.autoCompact", "true") \
                   .option("delta.dataSkippingNumIndexedCols", "32")
    
    # Write the table
    writer.save(path)
    
    # Create Delta table reference
    delta_table = DeltaTable.forPath(spark, path)
    
    # Set table properties
    spark.sql(f"""
        ALTER TABLE delta.`{path}`
        SET TBLPROPERTIES (
            'delta.minReaderVersion' = '2',
            'delta.minWriterVersion' = '5',
            'delta.columnMapping.mode' = 'name',
            'delta.enableChangeDataFeed' = 'true',
            'delta.tuneFileSizesForRewrites' = 'true',
            'delta.targetFileSize' = '128mb',
            'delta.checkpoint.writeStatsAsJson' = 'true',
            'delta.checkpoint.writeStatsAsStruct' = 'true'
        )
    """)
    
    # Apply Z-ordering if specified
    if z_order_cols:
        delta_table.optimize().executeZOrderBy(*z_order_cols)
    
    print(f"✅ Created Delta table: {table_name}")
    print(f"   - Path: {path}")
    print(f"   - Partitions: {partition_cols}")
    print(f"   - Z-order: {z_order_cols}")
    
    return delta_table

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Test Different Partitioning Strategies

# COMMAND ----------

# Create sample data for testing
def create_sample_fred_data(num_series=1000, days_back=365):
    """Create realistic FRED sample data"""
    
    from pyspark.sql import Row
    import random
    
    # Sample frequencies
    frequencies = ['D', 'W', 'M', 'Q', 'A']
    freq_weights = [0.3, 0.2, 0.3, 0.15, 0.05]
    
    # Generate series metadata
    series_data = []
    for i in range(num_series):
        freq = random.choices(frequencies, freq_weights)[0]
        series_data.append(Row(
            series_id=f"TEST{str(i).zfill(6)}",
            title=f"Test Economic Series {i}",
            observation_start=datetime.now().date() - timedelta(days=days_back),
            observation_end=datetime.now().date(),
            frequency=freq,
            seasonal_adjustment=random.choice(['SA', 'NSA', 'SAAR']),
            units=random.choice(['Percent', 'Index', 'Dollars', 'Thousands']),
            last_updated=datetime.now(),
            popularity=random.randint(1, 100),
            notes=f"Test series for Delta Lake optimization",
            category_id=random.randint(1, 100),
            release_id=random.randint(1, 50),
            source_id=random.randint(1, 10),
            collection_timestamp=datetime.now(),
            data_version=1
        ))
    
    series_df = spark.createDataFrame(series_data, series_metadata_schema)
    
    # Generate observations
    observations_data = []
    for series in series_data[:100]:  # First 100 series for testing
        # Generate time series based on frequency
        current_date = series.observation_start
        while current_date <= series.observation_end:
            observations_data.append(Row(
                series_id=series.series_id,
                date=current_date,
                value=random.uniform(50, 150) + random.gauss(0, 10),
                realtime_start=current_date,
                realtime_end=datetime.now().date(),
                collection_timestamp=datetime.now()
            ))
            
            # Increment based on frequency
            if series.frequency == 'D':
                current_date += timedelta(days=1)
            elif series.frequency == 'W':
                current_date += timedelta(days=7)
            elif series.frequency == 'M':
                current_date += timedelta(days=30)
            elif series.frequency == 'Q':
                current_date += timedelta(days=90)
            else:  # Annual
                current_date += timedelta(days=365)
    
    observations_df = spark.createDataFrame(observations_data, observations_schema)
    
    return series_df, observations_df

# Create test data
print("Creating sample FRED data...")
series_df, observations_df = create_sample_fred_data(1000, 730)  # 2 years of data
print(f"✅ Created {series_df.count()} series and {observations_df.count()} observations")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Test Different Table Organizations

# COMMAND ----------

# Test 1: Series metadata table (small, frequently accessed)
print("\n=== TEST 1: Series Metadata Table ===")
series_table = create_delta_table_with_properties(
    series_df,
    f"{TEST_PATH}/series_metadata",
    "series_metadata",
    partition_cols=["frequency"],  # Partition by frequency for common queries
    z_order_cols=["series_id", "popularity"]  # Z-order by ID and popularity
)

# Test 2: Observations table (large, time-series data)
print("\n=== TEST 2: Observations Table (Date Partitioned) ===")

# Add year and month columns for partitioning
observations_with_partitions = observations_df \
    .withColumn("year", year("date")) \
    .withColumn("month", month("date"))

obs_table_date = create_delta_table_with_properties(
    observations_with_partitions,
    f"{TEST_PATH}/observations_by_date",
    "observations_by_date",
    partition_cols=["year", "month"],  # Partition by time
    z_order_cols=["series_id", "date"]  # Z-order by series and date
)

# Test 3: Alternative - Observations partitioned by frequency
print("\n=== TEST 3: Observations Table (Frequency Partitioned) ===")

# Join with series to get frequency
observations_with_freq = observations_df.join(
    series_df.select("series_id", "frequency"),
    on="series_id",
    how="left"
).withColumn("year", year("date"))

obs_table_freq = create_delta_table_with_properties(
    observations_with_freq,
    f"{TEST_PATH}/observations_by_freq",
    "observations_by_freq",
    partition_cols=["frequency", "year"],  # Partition by frequency then year
    z_order_cols=["series_id", "date"]
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Performance Testing

# COMMAND ----------

def benchmark_query(query_name, query_func):
    """Benchmark a query and return execution time"""
    start_time = time.time()
    result = query_func()
    result.show(5, truncate=False)  # Force execution
    execution_time = time.time() - start_time
    
    print(f"\n📊 {query_name}")
    print(f"   Execution time: {execution_time:.2f} seconds")
    print(f"   Row count: {result.count()}")
    
    return execution_time

# Test queries
print("=== PERFORMANCE BENCHMARKS ===")

# Query 1: Get all daily series
benchmark_query(
    "Filter by frequency (Daily)",
    lambda: spark.read.format("delta").load(f"{TEST_PATH}/series_metadata")
        .filter(col("frequency") == "D")
)

# Query 2: Get observations for specific date range
benchmark_query(
    "Date range query (last 30 days)",
    lambda: spark.read.format("delta").load(f"{TEST_PATH}/observations_by_date")
        .filter(col("date") >= datetime.now().date() - timedelta(days=30))
)

# Query 3: Get popular series with recent data
benchmark_query(
    "Join query (popular series with observations)",
    lambda: spark.read.format("delta").load(f"{TEST_PATH}/series_metadata")
        .filter(col("popularity") > 80)
        .join(
            spark.read.format("delta").load(f"{TEST_PATH}/observations_by_date")
                .filter(col("date") >= datetime.now().date() - timedelta(days=7)),
            on="series_id"
        )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Delta Lake Optimization Techniques

# COMMAND ----------

# Demonstrate optimization techniques
print("=== DELTA OPTIMIZATION TECHNIQUES ===\n")

# 1. File compaction
print("1. Running OPTIMIZE for file compaction...")
spark.sql(f"OPTIMIZE delta.`{TEST_PATH}/observations_by_date`")
print("   ✅ Files compacted")

# 2. Z-Ordering optimization
print("\n2. Running Z-ORDER optimization...")
spark.sql(f"OPTIMIZE delta.`{TEST_PATH}/observations_by_date` ZORDER BY (series_id, date)")
print("   ✅ Z-ordering applied")

# 3. Vacuum old files
print("\n3. Running VACUUM to remove old files...")
spark.sql(f"VACUUM delta.`{TEST_PATH}/observations_by_date` RETAIN 168 HOURS")
print("   ✅ Old files removed")

# 4. Analyze table statistics
print("\n4. Analyzing table statistics...")
spark.sql(f"ANALYZE TABLE delta.`{TEST_PATH}/series_metadata` COMPUTE STATISTICS")
print("   ✅ Statistics computed")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Best Practices Summary for FRED Delta Lake

# COMMAND ----------

best_practices = """
# FRED DELTA LAKE BEST PRACTICES

## 1. Table Organization
- **Series Metadata**: Partition by frequency, Z-order by series_id and popularity
- **Observations**: Partition by year/month, Z-order by series_id and date
- **Categories**: No partitioning (small table), Z-order by category_id
- **Tags/Releases**: No partitioning, Z-order by primary key

## 2. Schema Design
- Use proper data types (DateType for dates, not strings)
- Include processing metadata (collection_timestamp, version)
- Design for evolution (use nullable fields where appropriate)

## 3. Partitioning Strategy
- Observations: year/month partitioning (balanced partition sizes)
- Series: frequency partitioning (aligns with query patterns)
- Avoid over-partitioning (target 1GB+ per partition)

## 4. Optimization Schedule
- OPTIMIZE daily for active partitions
- Z-ORDER weekly for frequently queried columns
- VACUUM weekly with 7-day retention

## 5. Table Properties
```sql
delta.autoOptimize.optimizeWrite = true
delta.autoOptimize.autoCompact = true
delta.targetFileSize = 128mb
delta.enableChangeDataFeed = true
```

## 6. Query Patterns
- Leverage partition pruning (filter on partition columns)
- Use Z-ordering columns in WHERE clauses
- Cache frequently accessed small tables

## 7. Storage Layout
```
/fred-delta-lake/
  /bronze/          # Raw data as collected
    /series/
    /observations/
  /silver/          # Cleaned, deduplicated
    /series_metadata/
    /observations/
  /gold/            # Aggregated, analytics-ready
    /series_summary/
    /indicators/
```
"""

print(best_practices)

# Save best practices
dbutils.fs.put(f"{TEST_PATH}/DELTA_LAKE_BEST_PRACTICES.md", best_practices, overwrite=True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Production Table Creation Script

# COMMAND ----------

# Generate production DDL scripts
production_ddl = """
-- FRED Production Delta Tables DDL

-- 1. Series Metadata Table
CREATE TABLE IF NOT EXISTS fred.series_metadata
USING DELTA
LOCATION '{storage_path}/silver/series_metadata'
PARTITIONED BY (frequency)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.targetFileSize' = '128mb'
);

-- 2. Observations Table
CREATE TABLE IF NOT EXISTS fred.observations
USING DELTA
LOCATION '{storage_path}/silver/observations'
PARTITIONED BY (year, month)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.targetFileSize' = '256mb'
);

-- 3. Categories Table
CREATE TABLE IF NOT EXISTS fred.categories
USING DELTA
LOCATION '{storage_path}/silver/categories'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.targetFileSize' = '64mb'
);

-- 4. Create optimized views
CREATE OR REPLACE VIEW fred.series_current AS
SELECT s.*, 
       o.latest_value,
       o.latest_date
FROM fred.series_metadata s
LEFT JOIN (
  SELECT series_id, 
         MAX(date) as latest_date,
         LAST(value) as latest_value
  FROM fred.observations
  GROUP BY series_id
) o ON s.series_id = o.series_id;
""".format(storage_path=STORAGE_PATH)

print(production_ddl)

# Save DDL
dbutils.fs.put(f"{TEST_PATH}/PRODUCTION_DDL.sql", production_ddl, overwrite=True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Monitoring and Maintenance

# COMMAND ----------

# Create monitoring queries
monitoring_queries = """
-- Table size monitoring
SELECT 
  'series_metadata' as table_name,
  COUNT(*) as row_count,
  SUM(size) / 1024 / 1024 / 1024 as size_gb
FROM (DESCRIBE DETAIL delta.`{path}/silver/series_metadata`);

-- Partition distribution
SELECT 
  frequency,
  COUNT(*) as series_count,
  AVG(file_size_mb) as avg_file_size_mb
FROM (
  SELECT frequency, size/1024/1024 as file_size_mb
  FROM delta.`{path}/silver/series_metadata`
)
GROUP BY frequency;

-- Query performance tracking
SELECT 
  query_id,
  query_text,
  execution_time_ms,
  rows_produced
FROM system.queries
WHERE query_text LIKE '%fred%'
ORDER BY execution_time_ms DESC
LIMIT 20;
"""

print("=== MONITORING QUERIES ===")
print(monitoring_queries.format(path=STORAGE_PATH))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Final Recommendations

# COMMAND ----------

final_recommendations = {
    "table_design": {
        "series_metadata": {
            "partition": "frequency",
            "z_order": ["series_id", "popularity"],
            "target_file_size": "128MB"
        },
        "observations": {
            "partition": ["year", "month"],
            "z_order": ["series_id", "date"],
            "target_file_size": "256MB"
        },
        "categories": {
            "partition": None,
            "z_order": ["category_id"],
            "target_file_size": "64MB"
        }
    },
    "maintenance_schedule": {
        "optimize": "daily",
        "z_order": "weekly",
        "vacuum": "weekly",
        "analyze": "weekly"
    },
    "query_patterns": {
        "use_partition_filters": True,
        "leverage_z_ordering": True,
        "cache_small_tables": True
    }
}

print("=== FINAL RECOMMENDATIONS ===")
print(json.dumps(final_recommendations, indent=2))

# Save recommendations
with open("/tmp/fred_delta_recommendations.json", "w") as f:
    json.dump(final_recommendations, f, indent=2)

print("\n✅ Test notebook complete!")
print(f"📁 Test data location: {TEST_PATH}")
print("📋 Next steps: Review results and implement in production")

# COMMAND ----------

# Cleanup test data (optional)
# dbutils.fs.rm(TEST_PATH, recurse=True)