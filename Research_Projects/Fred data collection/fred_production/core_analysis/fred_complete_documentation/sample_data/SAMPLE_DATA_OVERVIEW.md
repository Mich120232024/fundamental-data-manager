# Sample Data Overview

## Complete Datasets (100% collected)

### 1. sources_all.json
```json
{
  "sources": [
    {
      "id": 1,
      "name": "Board of Governors of the Federal Reserve System (US)",
      "link": "http://www.federalreserve.gov/"
    }
    // ... 91 total sources
  ]
}
```

### 2. releases_all.json
```json
{
  "releases": [
    {
      "id": 9,
      "name": "Advance Monthly Sales for Retail and Food Services",
      "press_release": true,
      "link": "http://www.census.gov/retail/marts/www/marts_current.pdf"
    }
    // ... 326 total releases
  ]
}
```

### 3. tags_complete.json
```json
{
  "tags": [
    {
      "name": "gdp",
      "group_id": "gen",
      "notes": "Gross Domestic Product",
      "popularity": 100,
      "series_count": 59862
    }
    // ... 8,000+ total tags
  ]
}
```

### 4. categories_complete_hierarchy.json
```json
{
  "categories": {
    "0": {
      "id": 0,
      "name": "Root",
      "parent_id": null,
      "children": [1, 32991, 10, 32992, 33060],
      "depth": 0,
      "is_leaf": false
    }
    // ... 5,183 total categories
  }
}
```

## Sample Responses by Endpoint Type

### Search Endpoint Example
**Endpoint**: `/fred/series/search?search_text=unemployment`
```json
{
  "seriess": [
    {
      "id": "UNRATE",
      "title": "Unemployment Rate",
      "frequency": "Monthly",
      "units": "Percent"
      // ... 15 total fields
    }
  ]
}
```

### Relationship Endpoint Example
**Endpoint**: `/fred/series/categories?series_id=GDP`
```json
{
  "categories": [
    {
      "id": 106,
      "name": "GDP",
      "parent_id": 18
    },
    {
      "id": 18,
      "name": "National Accounts",
      "parent_id": 32992
    }
  ]
}
```

### Tag Relationships Example
**Endpoint**: `/fred/related_tags?tag_names=inflation`
```json
{
  "tags": [
    {
      "name": "price",
      "group_id": "gen",
      "series_count": 15362,
      "popularity": 85
    },
    {
      "name": "indexes",
      "group_id": "gen", 
      "series_count": 15358,
      "popularity": 85
    }
    // ... up to 1000 per call
  ],
  "count": 758,  // Total available
  "limit": 1000,
  "offset": 0
}
```

### Series Metadata Example
**File**: sample_150_series_complete.json
```json
{
  "series_data": {
    "GDP": {
      "basic_info": {
        "id": "GDP",
        "title": "Gross Domestic Product",
        "frequency": "Quarterly",
        "units": "Billions of Dollars",
        "seasonal_adjustment": "Seasonally Adjusted Annual Rate",
        "observation_start": "1947-01-01",
        "observation_end": "2024-07-01",
        "last_updated": "2024-10-30 07:55:05-05",
        "popularity": 94,
        // ... all 15 fields
      }
    }
  }
}
```

## Key Patterns

### 1. Pagination Response
```json
{
  "data": [...],
  "count": 5918,    // Total available
  "limit": 1000,    // Current page size
  "offset": 0       // Current position
}
```

### 2. Error Response
```json
{
  "error_code": 400,
  "error_message": "Bad Request. Variable limit is not between 1 and 1000."
}
```

### 3. Rate Limit Response
```json
{
  "error_code": 429,
  "error_message": "Too Many Requests. Exceeded Rate Limit."
}
```

## Data Types Reference

### Frequencies
- Annual
- Semiannual  
- Quarterly
- Monthly
- Biweekly
- Weekly
- Daily
- 5-Year
- 10-Year

### Units (Common)
- Percent
- Billions of Dollars
- Index 2015=100
- Persons
- Thousands
- Number
- Dollars per Hour

### Seasonal Adjustments
- Not Seasonally Adjusted (NSA)
- Seasonally Adjusted (SA)
- Seasonally Adjusted Annual Rate (SAAR)