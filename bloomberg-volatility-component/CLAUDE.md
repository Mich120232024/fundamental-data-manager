# CLAUDE.md - Bloomberg Volatility Component

This file provides guidance to Claude Code when working with the Bloomberg volatility surface component.

## Project Overview

React + TypeScript application that displays real-time FX options volatility surfaces using Bloomberg Terminal data via an Azure VM API.

## Key Information

### Bloomberg API
- **URL**: http://20.172.249.92:8080
- **Auth**: Use `Authorization: Bearer test` header
- **Correct API file**: `main_checkpoint_working_2025_07_16.py`

### Critical Patterns

1. **NEVER use substring matching for tickers**
   ```javascript
   // WRONG - causes 35D to match 5D
   if (security.includes('5B1M'))
   
   // CORRECT - use regex
   const match = security.match(/EURUSD(\d+)(R|B)1M\s+BGN/)
   ```

2. **ON tenor is special**
   ```javascript
   // ATM for ON has no BGN
   isON ? `${pair}VON Curncy` : `${pair}V${tenor} BGN Curncy`
   ```

3. **Filter empty rows**
   - Many tenors return no data
   - Filter out rows where all values are null

### Known Issues

1. **1D/2D/3D tickers don't exist** - Use ON as shortest tenor
2. **Historical data requires YYYYMMDD format** - No hyphens
3. **Some tenors have no data** - This is normal, filter them out

### Testing Commands

```bash
# Check if API is running
curl http://20.172.249.92:8080/health

# Test a ticker
curl -X POST http://20.172.249.92:8080/api/bloomberg/reference \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"securities": ["EURUSD25R1M BGN Curncy"], "fields": ["PX_LAST", "PX_BID", "PX_ASK"]}'
```

### File Structure

```
/gzc-volatility-surface/
  /src/
    /api/bloomberg.ts         # API client - handles all Bloomberg data
    /components/
      VolatilitySurfaceContainer.tsx  # Main container with data fetching
      VolatilitySurfaceTable.tsx      # Table display component
```

## Important Rules

1. **Always test API changes with curl first**
2. **Log API responses during debugging**
3. **Use regex for ticker parsing, never substring matching**
4. **Filter empty data rows for clean display**
5. **Remember ON tenor has special formatting**

## Recent Context (Updated 2025-07-26)

### Major Architecture Changes
- **Removed ALL fallback data systems** - Application now shows real Bloomberg data only
- **Created local API gateway** (`bloomberg-gateway-enhanced.py`) with environment-based caching
- **Development mode**: `ENABLE_CACHE=false` ensures fresh Bloomberg data on every request
- **Fixed data flow**: Components now use correct `ValidatedVolatilityData` interface from `DataValidator.ts`

### API Behavior Discovery
- **Bloomberg API has fallback mode**: When Terminal is offline, serves comprehensive cached data
- **Timestamps are UTC**: Important for Greece users (UTC+3)
- **Session persistence**: API maintains connection even when Terminal UI shows login screen
- **Data validation**: API correctly validates tickers even in fallback mode

### UI/UX Improvements
- **Volatility Analysis Tab**: Complete rewrite with D3.js
  - Smile chart: Shows volatility curves by tenor
  - Term structure: Realistic time scaling (days to years)
  - Modern styling: Thin lines (1.2px), no visible points
  - Enhanced tooltips: Show strike type, tenor, volatility, time in days
- **3D Surface**: Updated hover template shows "Tenor", "Strike", "IV" instead of x,y,z
- **Data quality indicators**: Shows percentage of valid data received

### Technical Fixes
- Fixed type conflicts between two `ValidatedVolatilityData` interfaces
- Updated validation to handle null ATM values gracefully
- Fixed term structure x-axis to use linear time scale
- Removed `xScale.bandwidth()` check that broke linear scales
- All components now properly access `data.raw?.field` structure

### Development Workflow
```bash
# Local gateway (no cache)
python bloomberg-gateway-enhanced.py

# Frontend dev server
npm run dev

# Check real data flow
curl http://localhost:8000/health
```