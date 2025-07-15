# FRED API - Complete Endpoint Inventory

## All 31 Endpoints with Exact Status and Collection Methods

### 1. `/fred/sources`
- **What we have**: ✅ COMPLETE - 91 sources
- **File**: `fred_complete_data/sources_all.json` (24.6 KB)
- **Parameters**: None required
- **Method**: Single API call
- **Estimated full size**: 91 records (COMPLETE)

### 2. `/fred/source`
- **What we have**: ✅ SAMPLED - source_id=1
- **File**: `fred_samples/misc/07_source_detail.json`
- **Parameters**: `source_id` (required)
- **Method**: One call per source_id
- **Estimated full size**: 91 individual files (~2 MB total)

### 3. `/fred/source/releases`
- **What we have**: ✅ SAMPLED - source_id=1 releases
- **File**: `fred_samples/relationships/00_source_releases.json`
- **Parameters**: `source_id` (required)
- **Method**: One call per source × ~91 = 91 calls
- **Estimated full size**: ~30 KB per source = 2.7 MB total

### 4. `/fred/releases`
- **What we have**: ✅ COMPLETE - 326 releases
- **File**: `fred_complete_data/releases_all.json` (171.6 KB)
- **Parameters**: None required
- **Method**: Single API call
- **Estimated full size**: 326 records (COMPLETE)

### 5. `/fred/release`
- **What we have**: ✅ SAMPLED - release_id=51
- **File**: `fred_samples/misc/08_release_detail.json`
- **Parameters**: `release_id` (required)
- **Method**: One call per release × 326 = 326 calls
- **Estimated full size**: 326 individual files (~10 MB total)

### 6. `/fred/releases/dates`
- **What we have**: ✅ SAMPLED - 100 dates
- **File**: `fred_samples/foundation/04_release_dates_sample_100.json`
- **Parameters**: `realtime_start`, `realtime_end`, `limit`, `offset`
- **Method**: Pagination with limit=1000
- **Estimated full size**: ~50,000 dates, 50 API calls, ~5 MB

### 7. `/fred/release/dates`
- **What we have**: ✅ SAMPLED - release_id=82 dates
- **File**: `fred_samples/misc/09_release_dates_specific.json`
- **Parameters**: `release_id` (required)
- **Method**: One call per release × 326 = 326 calls
- **Estimated full size**: ~10 MB total

### 8. `/fred/release/series`
- **What we have**: ✅ SAMPLED - release_id=51 series
- **File**: `fred_samples/relationships/05_release_series.json`
- **Parameters**: `release_id` (required), `limit`, `offset`
- **Method**: Pagination per release, ~2,000 API calls total
- **Estimated full size**: ~100 MB (varies by release)

### 9. `/fred/release/sources`
- **What we have**: ✅ SAMPLED - release_id=13 sources
- **File**: `fred_samples/relationships/01_release_sources.json`
- **Parameters**: `release_id` (required)
- **Method**: One call per release × 326 = 326 calls
- **Estimated full size**: ~500 KB total

### 10. `/fred/release/tags`
- **What we have**: ✅ SAMPLED - release_id=51 tags
- **File**: `fred_samples/relationships/06_release_tags.json`
- **Parameters**: `release_id` (required), `limit`, `offset`
- **Method**: Pagination per release, ~500 API calls
- **Estimated full size**: ~20 MB total

### 11. `/fred/release/related_tags`
- **What we have**: ✅ SAMPLED - release_id=86, tag_names=sa
- **File**: `fred_samples/relationships/07_release_related_tags.json`
- **Parameters**: `release_id` (required), `tag_names` (required)
- **Method**: Complex - depends on tag combinations
- **Estimated full size**: ~50 MB for common combinations

### 12. `/fred/release/tables`
- **What we have**: ✅ SAMPLED - release_id=53 (GDP)
- **File**: `fred_samples/misc/10_release_tables.json`
- **Parameters**: `release_id` (required), `element_id`
- **Method**: Multiple calls per release
- **Estimated full size**: ~100 MB (complex structures)

### 13. `/fred/categories`
- **What we have**: ✅ COMPLETE - 5,183 categories
- **File**: `fred_complete_data/categories_complete_hierarchy.json` (1.81 MB)
- **Parameters**: None (we collected all via traversal)
- **Method**: Recursive traversal from root
- **Estimated full size**: 5,183 records (COMPLETE)

### 14. `/fred/category`
- **What we have**: ✅ SAMPLED - category_id=32073
- **File**: `fred_samples/hierarchical/00_category_detail.json`
- **Parameters**: `category_id` (required)
- **Method**: One call per category × 5,183 = 5,183 calls
- **Estimated full size**: ~50 MB total

### 15. `/fred/category/children`
- **What we have**: ✅ COMPLETE (in hierarchy)
- **File**: Integrated in `categories_complete_hierarchy.json`
- **Parameters**: `category_id` (required)
- **Method**: Recursive traversal (already done)
- **Estimated full size**: Included in categories file

### 16. `/fred/category/related`
- **What we have**: ✅ SAMPLED - category_id=32073
- **File**: `fred_samples/hierarchical/02_category_related.json`
- **Parameters**: `category_id` (required)
- **Method**: One call per category × 5,183 = 5,183 calls
- **Estimated full size**: ~30 MB total

### 17. `/fred/category/series`
- **What we have**: ✅ SAMPLED - Multiple categories
- **File**: `fred_samples/hierarchical/03_category_series.json`
- **Parameters**: `category_id` (required), `limit`, `offset`
- **Method**: Pagination per category, ~50,000 API calls
- **Estimated full size**: ~2 GB (main discovery method)

### 18. `/fred/category/tags`
- **What we have**: ✅ SAMPLED - category_id=125
- **File**: `fred_samples/hierarchical/04_category_tags.json`
- **Parameters**: `category_id` (required), `limit`, `offset`
- **Method**: Pagination per category, ~10,000 API calls
- **Estimated full size**: ~100 MB total

### 19. `/fred/category/related_tags`
- **What we have**: ✅ SAMPLED - category_id=125, tag_names=usa
- **File**: `fred_samples/hierarchical/05_category_related_tags.json`
- **Parameters**: `category_id` (required), `tag_names` (required)
- **Method**: Complex - depends on combinations
- **Estimated full size**: ~200 MB for common combinations

### 20. `/fred/tags`
- **What we have**: ✅ COMPLETE - 8,000+ tags
- **File**: `fred_complete_data/tags_complete.json` (1.09 MB)
- **Parameters**: `limit`, `offset`
- **Method**: Pagination with limit=1000, 9 API calls
- **Estimated full size**: 8,000+ records (COMPLETE)

### 21. `/fred/tags/series`
- **What we have**: ✅ SAMPLED - tag=slovenia
- **File**: `fred_samples/misc/05_tags_series.json`
- **Parameters**: `tag_names` (required), `limit`, `offset`
- **Method**: Pagination per tag, ~30,000 API calls
- **Estimated full size**: ~1 GB total

### 22. `/fred/related_tags` 🟢 WORKING
- **What we have**: ✅ SAMPLED + LOCAL - Multiple tags
- **Files**: 
  - `fred_samples/relationships/10_related_tags_inflation_cpi.json`
  - `fred_data_local/tags/related_tags_*.json` (7 files)
- **Parameters**: `tag_names` (required), `limit`, `offset`
- **Method**: Pagination per tag, limit=1000, ~30,000 API calls
- **Estimated full size**: ~2-3 GB (16.4M relationships)

### 23. `/fred/tags/related` 🔴 NOT WORKING
- **What we have**: ❌ 404 ERROR
- **Status**: Returns {"error_code":404,"error_message":"Not Found"}
- **Alternative**: Use `/fred/related_tags`

### 24. `/fred/series`
- **What we have**: ✅ SAMPLED - 150 series
- **File**: `fred_complete_data/sample_150_series_complete.json` (231.9 KB)
- **Parameters**: `series_id` (required)
- **Method**: One call per series × 800,000 = 800,000 calls
- **Estimated full size**: ~2 GB for all series

### 25. `/fred/series/search` 🔵 SEARCH
- **What we have**: ✅ SAMPLED - search=unemployment
- **File**: `fred_samples/series/01_series_search.json`
- **Parameters**: `search_text` (required), `limit`, `offset`
- **Method**: Depends on search terms
- **Estimated full size**: Variable

### 26. `/fred/series/search/tags` 🔵 SEARCH
- **What we have**: ✅ SAMPLED - tags=gdp;quarterly
- **File**: `fred_samples/series/02_series_search_tags.json`
- **Parameters**: `tag_names` (required), `limit`, `offset`
- **Method**: Depends on tag combinations
- **Estimated full size**: Variable

### 27. `/fred/series/search/related_tags` 🔵 SEARCH
- **What we have**: ✅ SAMPLED - search=inflation, tag_names=cpi
- **File**: `fred_samples/series/03_series_search_related_tags.json`
- **Parameters**: `search_text`, `tag_names` (required)
- **Method**: Complex search combinations
- **Estimated full size**: Variable

### 28. `/fred/series/updates` 🟠 SPECIAL
- **What we have**: ✅ SAMPLED - filter_value=all
- **File**: `fred_samples/series/04_series_updates.json`
- **Parameters**: `filter_value`, `start_time`, `end_time`
- **Method**: For incremental updates
- **Estimated full size**: Depends on time range

### 29. `/fred/series/categories`
- **What we have**: ✅ SAMPLED - series_id=GDP
- **File**: `fred_samples/series/06_series_categories.json`
- **Parameters**: `series_id` (required)
- **Method**: One call per series × 800,000 = 800,000 calls
- **Estimated full size**: ~500 MB total

### 30. `/fred/series/release`
- **What we have**: ✅ SAMPLED - series_id=GDP
- **File**: `fred_samples/series/07_series_release.json`
- **Parameters**: `series_id` (required)
- **Method**: One call per series × 800,000 = 800,000 calls
- **Estimated full size**: ~300 MB total

### 31. `/fred/series/tags`
- **What we have**: ✅ SAMPLED - series_id=GDP
- **File**: `fred_samples/series/08_series_tags.json`
- **Parameters**: `series_id` (required)
- **Method**: One call per series × 800,000 = 800,000 calls
- **Estimated full size**: ~1 GB total

---

## TOTAL COLLECTION ESTIMATES

### API Calls Required for Complete Collection:
- Series discovery: ~50,000 calls
- Series metadata (4 endpoints × 800,000): ~3.2M calls
- Tag relationships: ~30,000 calls
- Other relationships: ~20,000 calls
- **TOTAL**: ~3.3 million API calls

### Time Estimate:
- At 120 calls/minute = 27,500 minutes = 458 hours
- With 10 parallel workers = ~46 hours

### Storage Estimate:
- Complete metadata: ~10-15 GB uncompressed
- Delta Lake compressed: ~3-5 GB