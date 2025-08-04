# Database Cleanup Impact Analysis

## What Was Removed
- `currency_pairs` table (25 rows)
- `bloomberg_tickers_new` table (27 rows)
- 5 other empty duplicate tables

## Current State
- Single `bloomberg_tickers` table with 1,035 tickers
- Contains 527 FX forward tickers
- All data preserved and backed up

## Application Impact

### API Endpoints Available
- `/api/bloomberg/reference` ✅
- `/api/bloomberg/historical` ✅
- `/api/bloomberg/ticker-discovery` ✅
- `/api/fx/rates/live` ✅
- `/health` ✅

### Missing Endpoint
- `/api/fx-forwards/curves` ❌ (used by FX Forward Curves Tab)

## Component Analysis

The FX Forward Curves Tab expects:
- Endpoint: `/api/fx-forwards/curves`
- Payload: `{currency_pairs: [...], display_mode: "outright", max_tenor: "3Y"}`

This endpoint doesn't exist on the Bloomberg API, suggesting it was:
1. A local backend endpoint that queried currency_pairs table
2. Never fully implemented
3. Part of a different service

## Fix Options

1. **Quick Fix**: Update FXForwardCurvesTab.tsx to use existing endpoints
2. **Proper Fix**: Create backend endpoint that queries bloomberg_tickers for FX forward data
3. **Temporary**: Hardcode currency pairs like other tabs do

The database consolidation is correct - we just discovered an incomplete integration.