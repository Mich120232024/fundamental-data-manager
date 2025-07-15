# FRED Series Collection Strategy
**Building on Excellent Category Tree Foundation**

## **🎯 OBJECTIVE**
Use our complete leaf category tree (4,798 categories) to systematically collect series metadata and ultimately get full count of FRED series.

## **📊 FOUNDATION ASSETS**
✅ **categories_leaf_only.json** - 47,985 lines, 4,798 leaf categories  
✅ **Structured data** - id, name, parent_id, depth, confirmed leaf status  
✅ **Complete hierarchy** - Full parent relationships mapped  
✅ **Proven methodology** - Small tasks, complete execution

---

## **🚀 PHASE 1: SERIES COUNT SURVEY**
**Goal:** Get series count for each leaf category to understand scope

### **Step 1A: Sample Category Series Count (START HERE)**
```python
# Test with 10 categories first - small focused task
sample_categories = [32145, 32250, 33500, 33001, 33509]
# GET /fred/category/series?category_id={id}&limit=1
# Extract series_count from metadata, don't download series
```

**Expected Output:**
```json
{
  "category_series_counts": {
    "32145": {"name": "Foreign Exchange Intervention", "series_count": 47},
    "32250": {"name": "ADP Employment", "series_count": 234},
    ...
  }
}
```

### **Step 1B: Scale to All Categories**
- Process in batches of 50 categories
- Rate limit: 1 call per second (3,600/hour max)
- Complete survey in ~2 hours runtime
- Track progress and checkpoint

---

## **🔢 PHASE 2: SERIES METADATA COLLECTION**
**Goal:** Collect metadata for series in high-value categories

### **Step 2A: Prioritize Categories**
Based on series counts from Phase 1:
1. **High-volume categories** (>1000 series) - Core economic data
2. **Medium categories** (100-1000 series) - Sector-specific data  
3. **Specialized categories** (<100 series) - Niche indicators

### **Step 2B: Metadata Collection**
```python
# For each priority category:
# GET /fred/category/series?category_id={id}&limit=1000
# Collect: id, title, frequency, units, last_updated, notes
# Store in structured batches
```

---

## **⚡ PHASE 3: SELECTIVE OBSERVATIONS**
**Goal:** Collect time series data for strategic indicators

### **Step 3A: Identify Key Series**
- Popular series (high observation counts)
- Recent data (last_updated within 1 year)
- Core economic indicators (GDP, employment, inflation)

### **Step 3B: Observations Collection**
```python
# For selected series:
# GET /fred/series/observations?series_id={id}
# Store in time-based partitions
```

---

## **🎯 EXECUTION STRATEGY**

### **Claude Task Design:**
1. **Single category batch** (10-50 categories)
2. **Clear success criteria** (JSON output with specific structure)
3. **Error handling** (retry logic, rate limiting)
4. **Progress tracking** (checkpoint files)
5. **Quality validation** (schema compliance)

### **File Organization:**
```
fred_series_collection/
├── phase1_counts/
│   ├── batch_001_categories_1-50.json
│   ├── batch_002_categories_51-100.json
│   └── series_count_summary.json
├── phase2_metadata/
│   ├── high_volume/
│   ├── medium_volume/
│   └── specialized/
└── phase3_observations/
    ├── monthly/
    ├── quarterly/
    └── annual/
```

---

## **💰 AZURE PREPARATION**

While collecting locally, design for eventual Azure deployment:

### **Data Structure:**
- **Hierarchical partitioning** (year/month/day)
- **Delta Lake compatible** schema
- **Event-driven triggers** for new data

### **Processing Pattern:**
- **Category-based workers** (parallel processing)
- **Series-based storage** (optimized for queries)
- **Incremental updates** (only new/changed data)

---

## **🚀 IMMEDIATE NEXT STEP**

**START WITH PHASE 1A:**
Create script to get series counts for first 10 leaf categories:
- Categories: 32145, 32250, 33500, 33001, 33509, 33831, 32240, 33731, 5, 32262
- Output: JSON with category_id, name, series_count
- Runtime: <60 seconds
- Success criteria: All 10 categories processed successfully

**This builds directly on your excellent category tree and follows your proven small-task methodology!** 