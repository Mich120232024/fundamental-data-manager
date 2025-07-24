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

## Recent Context

- Fixed substring matching bug that caused data misalignment
- Added filtering for empty tenor rows
- Discovered 1D/2D/3D tickers don't exist in Bloomberg FX options
- Implemented historical data selection with proper date formatting
- Added Historical Analysis tab with time series table view
- Tab navigation between Surface and Historical views
- Added Smile Analysis tab with lightweight-charts for volatility smile visualization
- Implemented 4-quadrant dashboard: smile curve, key metrics, term structure, trading signals
- Installed lightweight-charts for GZC Intel app compatibility