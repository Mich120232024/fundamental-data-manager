# FRED API Collection Methods

## Method 1: Single Call (No Parameters)
**Used for**: `/fred/sources`, `/fred/releases`, `/fred/tags`, `/fred/categories`

```python
response = api_call(endpoint)
# Returns complete dataset in one call
```

## Method 2: Simple Iteration (One Parameter)
**Used for**: Detail endpoints like `/fred/source`, `/fred/release`, `/fred/category`, `/fred/series`

```python
for entity_id in all_entity_ids:
    response = api_call(endpoint, {'entity_id': entity_id})
    # One call per entity
```

## Method 3: Pagination (Large Results)
**Used for**: `/fred/tags`, `/fred/related_tags`, `/fred/category/series`, etc.

```python
offset = 0
limit = 1000  # Maximum allowed
while True:
    response = api_call(endpoint, {
        'parameter': value,
        'limit': limit,
        'offset': offset
    })
    if len(response['data']) < limit:
        break
    offset += limit
```

## Method 4: Hierarchical Traversal
**Used for**: `/fred/category/children`

```python
def traverse_categories(parent_id=0):
    children = api_call('/category/children', {'category_id': parent_id})
    for child in children:
        # Process child
        traverse_categories(child['id'])  # Recursive
```

## Method 5: Discovery Pattern
**Used for**: Finding all series

```python
# Step 1: Get all categories
categories = load_categories()

# Step 2: For each leaf category, get series
for category in leaf_categories:
    series = api_call('/category/series', {
        'category_id': category['id'],
        'limit': 1000,
        'offset': 0  # Paginate as needed
    })
```

## Method 6: Relationship Mapping
**Used for**: Building complete graph

```python
# For each entity, get its relationships
for series_id in all_series:
    categories = api_call('/series/categories', {'series_id': series_id})
    tags = api_call('/series/tags', {'series_id': series_id})
    release = api_call('/series/release', {'series_id': series_id})
    # Store relationships
```

## Method 7: Two-Parameter Combinations
**Used for**: `/fred/category/related_tags`, `/fred/release/related_tags`

```python
for category_id in categories:
    for tag_name in common_tags:
        response = api_call('/category/related_tags', {
            'category_id': category_id,
            'tag_names': tag_name
        })
```

## Method 8: Time-Based Collection
**Used for**: `/fred/series/updates`

```python
# Daily incremental updates
response = api_call('/series/updates', {
    'filter_value': 'all',
    'start_time': yesterday,
    'end_time': today
})
```

## Rate Limiting Strategy

### Adaptive Rate Limiting
```python
MIN_SLEEP = 0.5
MAX_SLEEP = 1.0
current_sleep = MIN_SLEEP

if response.status_code == 200:
    current_sleep = max(MIN_SLEEP, current_sleep * 0.95)
elif response.status_code == 429:
    current_sleep = min(MAX_SLEEP, current_sleep * 1.5)
    time.sleep(30)  # Wait for rate limit reset
```

### Parallel Collection
```python
# Use 10 workers for different categories
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for category in categories:
        future = executor.submit(collect_category_data, category)
        futures.append(future)
```

## Checkpointing Pattern

```python
def save_checkpoint(state):
    with open('checkpoint.json', 'w') as f:
        json.dump(state, f)

def load_checkpoint():
    if os.path.exists('checkpoint.json'):
        with open('checkpoint.json', 'r') as f:
            return json.load(f)
    return {'completed': [], 'last_index': 0}

# Use in collection
checkpoint = load_checkpoint()
for i, item in enumerate(items[checkpoint['last_index']:]):
    # Process item
    checkpoint['completed'].append(item['id'])
    checkpoint['last_index'] = i
    save_checkpoint(checkpoint)
```

## Storage Pattern

### Individual Files
```python
# For entity details
safe_filename = entity_id.replace('/', '_').replace(':', '_')
with open(f'data/{entity_type}/{safe_filename}.json', 'w') as f:
    json.dump(data, f)
```

### Batch Storage
```python
# For relationships
batch_data = []
for item in items:
    batch_data.append(process_item(item))
    if len(batch_data) >= 1000:
        write_to_delta_lake(batch_data)
        batch_data = []
```

---

## Estimated Time by Method

| Method | API Calls | Time | Parallel Time |
|--------|-----------|------|---------------|
| Single Call | 4 | < 1 min | N/A |
| Simple Iteration | ~1,000 | 15 min | 2 min |
| Pagination | ~50,000 | 7 hours | 45 min |
| Discovery | ~100,000 | 14 hours | 1.5 hours |
| Full Relationships | ~3.2M | 450 hours | 45 hours |