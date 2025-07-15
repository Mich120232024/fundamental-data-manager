# FRED Azure Quality Standards

## 🎯 Delta Lake Data Quality Standards

### 1. Data Completeness Standards

**Categories Table**
```sql
-- Every category must have:
- id: NOT NULL, UNIQUE
- name: NOT NULL, length > 0
- parent_id: NULL only for root (id=0)
- All parent_ids must exist in the table
- No circular references
```

**Series Table**
```sql
-- Every series must have:
- series_id: NOT NULL, UNIQUE, matches FRED format
- title: NOT NULL
- units: NOT NULL
- frequency: IN ('D', 'W', 'BW', 'M', 'Q', 'SA', 'A', 'NA')
- last_updated: NOT NULL, valid timestamp
- At least one category relationship
- Valid release_id if not unreleased
```

**Relationships**
```sql
-- Series-Category: Every series in at least 1 category
-- Series-Tags: Orphan tags not allowed
-- Series-Release: Must match valid release or be null
```

### 2. Data Integrity Rules

**Referential Integrity**
- No foreign key can reference non-existent entity
- Deletes must cascade or be blocked
- Updates must maintain consistency

**Business Logic Integrity**
- Series frequency must match observation patterns
- Release dates must be valid for series
- Seasonal adjustments only for appropriate frequencies

### 3. Delta Lake Specific Standards

**Table Properties**
```sql
ALTER TABLE silver.fred_series SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.dataSkippingNumIndexedCols' = '32',
  'delta.checkpoint.writeStatsAsStruct' = 'true',
  'delta.checkpoint.writeStatsAsJson' = 'false'
);
```

**Data Quality Constraints**
```sql
ALTER TABLE silver.fred_series ADD CONSTRAINT valid_frequency 
  CHECK (frequency IN ('D', 'W', 'BW', 'M', 'Q', 'SA', 'A', 'NA'));

ALTER TABLE silver.fred_series ADD CONSTRAINT series_id_format 
  CHECK (LENGTH(series_id) > 0 AND series_id = UPPER(series_id));
```

### 4. Merge Standards for Updates

```sql
MERGE INTO silver.fred_series target
USING updates source
ON target.series_id = source.series_id
WHEN MATCHED AND source.last_updated > target.last_updated THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *;
```

## 🏭 Production Engine Quality Standards

### 1. Processing Standards

**Idempotency**
- Every operation must be safely repeatable
- Same input = same output always
- No side effects on retry

**Transaction Boundaries**
```python
def process_batch(batch_id):
    try:
        # Start transaction
        spark.sql("BEGIN TRANSACTION")
        
        # Process data
        validate_data(batch_id)
        transform_data(batch_id)
        load_to_delta(batch_id)
        
        # Commit only if all succeed
        spark.sql("COMMIT")
    except Exception as e:
        spark.sql("ROLLBACK")
        log_error(batch_id, e)
        raise
```

### 2. Validation Framework

**Pre-Processing Validation**
```python
class FREDValidator:
    def validate_batch(self, df):
        validations = [
            self.check_required_columns,
            self.check_data_types,
            self.check_value_ranges,
            self.check_referential_integrity,
            self.check_business_rules
        ]
        
        for validation in validations:
            result = validation(df)
            if not result.passed:
                raise ValidationError(result.message)
```

**Post-Processing Validation**
```python
def validate_delta_write(table_name, expected_count):
    actual_count = spark.table(table_name).count()
    assert actual_count >= expected_count * 0.99  # 99% threshold
    
    # Check for duplicates
    duplicates = spark.sql(f"""
        SELECT series_id, COUNT(*) as cnt 
        FROM {table_name} 
        GROUP BY series_id 
        HAVING cnt > 1
    """)
    assert duplicates.count() == 0
```

### 3. Error Handling Standards

**Error Classification**
```python
class ErrorSeverity(Enum):
    CRITICAL = "CRITICAL"  # Stop processing
    ERROR = "ERROR"        # Skip record, continue
    WARNING = "WARNING"    # Log and continue
    INFO = "INFO"          # Informational only
```

**Error Recovery**
```python
def process_with_recovery(batch):
    max_retries = 3
    retry_delay = 60  # seconds
    
    for attempt in range(max_retries):
        try:
            return process_batch(batch)
        except TransientError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            raise
        except CriticalError:
            # No retry for critical errors
            raise
```

### 4. Monitoring Standards

**Key Metrics**
```python
metrics = {
    "data_quality": {
        "null_rate": "< 0.1%",
        "duplicate_rate": "= 0%",
        "orphan_rate": "= 0%",
        "validation_pass_rate": "> 99.9%"
    },
    "processing": {
        "success_rate": "> 99.5%",
        "latency_p99": "< 5 minutes",
        "error_rate": "< 0.5%",
        "retry_rate": "< 5%"
    },
    "data_freshness": {
        "update_lag": "< 1 hour",
        "processing_delay": "< 15 minutes"
    }
}
```

**Health Checks**
```python
class HealthCheck:
    def check_data_freshness(self):
        latest = spark.sql("""
            SELECT MAX(last_updated) as latest 
            FROM silver.fred_series
        """).collect()[0]['latest']
        
        hours_old = (datetime.now() - latest).total_seconds() / 3600
        return hours_old < 24  # Fail if > 24 hours old
    
    def check_completeness(self):
        # Categories should never decrease
        current_count = spark.table("silver.fred_categories").count()
        return current_count >= 5183
```

### 5. Audit Standards

**Every Process Must Log**
```json
{
  "process_id": "uuid",
  "process_name": "series_update",
  "start_time": "2025-01-15T10:00:00Z",
  "end_time": "2025-01-15T10:05:00Z",
  "records_processed": 1000,
  "records_updated": 150,
  "records_failed": 0,
  "validation_results": {},
  "error_details": []
}
```

### 6. Change Data Capture

**Track All Changes**
```sql
ALTER TABLE silver.fred_series 
SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- Query changes
SELECT * FROM table_changes('silver.fred_series', 2);
```

## 📊 Quality Gates

### Gate 1: Source Data Validation
- ✓ API response schema matches expected
- ✓ No critical fields missing
- ✓ Data types correct

### Gate 2: Transformation Validation  
- ✓ All business rules applied
- ✓ No data loss during transformation
- ✓ Relationships maintained

### Gate 3: Delta Lake Write Validation
- ✓ Transaction completed successfully
- ✓ Row counts match expected
- ✓ No constraint violations

### Gate 4: Post-Process Validation
- ✓ Data queryable and correct
- ✓ Statistics updated
- ✓ No orphaned data

## 🚨 Alerting Thresholds

**Critical Alerts**
- Data > 24 hours old
- Any CRITICAL errors
- Validation pass rate < 99%
- Process failures > 3 consecutive

**Warning Alerts**
- Retry rate > 10%
- Processing time > 2x normal
- Null rate > 1%
- Queue depth > 10,000

**Info Alerts**
- Daily summary statistics
- Weekly quality report
- Monthly trend analysis