# FRED API Endpoints - Color Coded by Type

## 🟢 FOUNDATION ENDPOINTS (Complete Data Available)
These return complete datasets without parameters:

| Endpoint | Status | Records | Our File |
|----------|--------|---------|----------|
| `/fred/sources` | ✅ COMPLETE | 91 | `sources_all.json` |
| `/fred/releases` | ✅ COMPLETE | 326 | `releases_all.json` |
| `/fred/tags` | ✅ COMPLETE | 8,000+ | `tags_complete.json` |
| `/fred/categories` | ✅ COMPLETE | 5,183 | `categories_complete_hierarchy.json` |

## 🔵 SEARCH ENDPOINTS (Dynamic Results)
These provide search capabilities with variable results:

| Endpoint | Purpose | Required Parameters | Special Notes |
|----------|---------|-------------------|---------------|
| `/fred/series/search` | Text search | `search_text` | Free text search |
| `/fred/series/search/tags` | Tag-based search | `tag_names` | Semicolon-separated tags |
| `/fred/series/search/related_tags` | Combined search | `search_text`, `tag_names` | Most complex search |
| `/fred/tags/series` | Series by tag | `tag_names` | Can return thousands |

## 🟣 RELATIONSHIP ENDPOINTS (Graph/Mapping Data)
These reveal connections between entities:

| Endpoint | Maps | Key Parameters | Pagination |
|----------|------|----------------|------------|
| `/fred/related_tags` | Tag → Tags | `tag_names` | Yes (limit=1000) |
| `/fred/category/series` | Category → Series | `category_id` | Yes |
| `/fred/category/tags` | Category → Tags | `category_id` | Yes |
| `/fred/category/related` | Category → Categories | `category_id` | No |
| `/fred/release/series` | Release → Series | `release_id` | Yes |
| `/fred/release/tags` | Release → Tags | `release_id` | Yes |
| `/fred/series/categories` | Series → Categories | `series_id` | No |
| `/fred/series/release` | Series → Release | `series_id` | No |
| `/fred/series/tags` | Series → Tags | `series_id` | No |
| `/fred/source/releases` | Source → Releases | `source_id` | No |

## 🟠 SPECIAL/COMPLEX ENDPOINTS
These have unique behaviors or data structures:

| Endpoint | Special Feature | Notes |
|----------|----------------|-------|
| `/fred/series/updates` | Time-based filtering | For incremental updates |
| `/fred/release/tables` | Complex nested structure | Returns formatted tables |
| `/fred/series/vintagedates` | Historical revisions | Returns date array |
| `/fred/releases/dates` | All release calendar | Massive date list |
| `/fred/category/related_tags` | Requires TWO parameters | `category_id` + `tag_names` |
| `/fred/release/related_tags` | Requires TWO parameters | `release_id` + `tag_names` |

## 🟡 DETAIL ENDPOINTS (Individual Records)
These return details for single entities:

| Endpoint | Entity | Parameter |
|----------|--------|-----------|
| `/fred/source` | Source details | `source_id` |
| `/fred/release` | Release details | `release_id` |
| `/fred/category` | Category details | `category_id` |
| `/fred/series` | Series details | `series_id` |

## 🔴 DEPRECATED/NOT WORKING
| Endpoint | Status | Alternative |
|----------|--------|-------------|
| `/fred/tags/related` | 404 Error | Use `/fred/related_tags` |

## ⚫ OUT OF SCOPE
| Endpoint | Reason |
|----------|--------|
| `/fred/series/observations` | User: "ignore the observations for now" |

---

## Collection Priority by Color:
1. 🟢 **Green** - Already complete! ✅
2. 🟣 **Purple** - Critical for relationships
3. 🟡 **Yellow** - Needed for complete metadata
4. 🔵 **Blue** - On-demand search capabilities
5. 🟠 **Orange** - Special use cases