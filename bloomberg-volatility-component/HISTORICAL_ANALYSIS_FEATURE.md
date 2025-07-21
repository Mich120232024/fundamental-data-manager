# Historical Volatility Analysis Feature

## Overview

The Historical Analysis feature provides time series analysis of FX option volatilities, allowing traders to track volatility evolution over configurable time periods.

## Features

### 1. Tab Navigation
- Clean tab interface at the top of the application
- Two tabs: "Volatility Surface" and "Historical Analysis"
- Maintains state when switching between tabs

### 2. Historical Data Table
- Displays volatility data in chronological order (most recent first)
- Shows complete volatility smile components:
  - ATM volatility
  - Risk Reversals (5D, 10D, 15D, 25D, 35D)
  - Butterflies (5D, 10D, 15D, 25D, 35D)

### 3. Configurable Parameters

#### Currency Pair Selection
- All 28 major FX pairs available
- Same pairs as in Surface view for consistency

#### Tenor Selection
- Select specific tenor for analysis
- Available tenors: ON, 1W, 2W, 3W, 1M, 2M, 3M, 4M, 6M, 9M, 1Y, 18M, 2Y

#### Date Range Options
- Last 7 days
- Last 30 days (default)
- Last 60 days
- Last 90 days
- Last 180 days
- Last 1 year
- Last 2 years

### 4. Visual Design
- Consistent with GZC Intel app styling
- Sticky headers for easy reference when scrolling
- Color coding for risk reversals:
  - Green for positive values
  - Red for negative values
- Monospace font for numerical data
- Alternating row colors for readability

## Technical Implementation

### Data Fetching
- Uses Bloomberg `/api/bloomberg/historical` endpoint
- Fetches all components in parallel for efficiency
- Date format: YYYYMMDD
- Fields: PX_LAST (for historical analysis)

### Data Processing
1. Fetches each volatility component separately
2. Combines data by date
3. Sorts by date (most recent first)
4. Displays in table format

### Component Structure
```
MainAppContainer
├── Tab Navigation
└── Content Area
    ├── VolatilitySurfaceContainer (Surface tab)
    └── VolatilityHistoricalTable (Historical tab)
```

## Usage Examples

### Analyzing Volatility Trends
1. Select "Historical Analysis" tab
2. Choose currency pair (e.g., EURUSD)
3. Select tenor (e.g., 1M)
4. Choose date range (e.g., Last 30 days)
5. Click "Refresh" to load data

### Comparing Different Tenors
1. Load data for one tenor
2. Note key levels and trends
3. Change tenor selection
4. Compare how different tenors behaved

### Event Analysis
1. Select appropriate date range covering the event
2. Look for volatility spikes or changes
3. Analyze risk reversal behavior during events
4. Check butterfly movements for tail risk pricing

## API Usage

### Request Format
```javascript
// For each component:
POST /api/bloomberg/historical
{
  "security": "EURUSD25R1M BGN Curncy",
  "fields": ["PX_LAST"],
  "start_date": "20250101",
  "end_date": "20250131",
  "periodicity": "DAILY"
}
```

### Response Processing
- Combines multiple security responses by date
- Handles missing data gracefully
- Formats dates for display

## Performance Considerations

1. **Parallel Fetching**: All securities fetched simultaneously
2. **Data Caching**: Browser caches responses automatically
3. **Efficient Rendering**: Table virtualization for large datasets
4. **Minimal Re-renders**: React optimization with proper keys

## Future Enhancements

1. **Export Functionality**: CSV/Excel export for further analysis
2. **Statistical Metrics**: Mean, standard deviation, percentiles
3. **Charting Option**: Optional chart view for visual analysis
4. **Multi-tenor Comparison**: Compare multiple tenors side-by-side
5. **Change Calculations**: Day-over-day, week-over-week changes
6. **Volatility Smile Reconstruction**: Calculate full smile from components