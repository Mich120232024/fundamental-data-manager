# CLAUDE.md - Bloomberg Volatility Component

This file provides guidance to Claude Code when working with the Bloomberg volatility surface component.

## Project Overview

React + TypeScript application that displays real-time FX options volatility surfaces using Bloomberg Terminal data via an Azure VM API.

## Key Information

### Bloomberg API
- **URL**: http://20.172.249.92:8080
- **Type**: FastAPI application with full Swagger docs at `/docs`
- **Auth**: Use `Authorization: Bearer test` header
- **Server**: `C:\BloombergAPI\main.py` on bloomberg-vm-02
- **IMPORTANT**: Always use local gateway at localhost:8000 (bloomberg-gateway-enhanced.py)

### Available Endpoints (Updated 2025-07-30)
- **POST /api/bloomberg/reference** - Get reference data for securities
- **POST /api/bloomberg/historical** - Get historical time series data  
- **GET /api/fx/rates/live** - Get live FX rates
- **POST /api/bloomberg/ticker-discovery** - ✅ OPERATIONAL - Search for tickers by type/currency
- **POST /api/bloomberg/validate-tickers** - ✅ OPERATIONAL - Batch ticker validation with live prices

### CRITICAL: Generic Endpoint Pattern (Updated 2025-08-04)
**ALWAYS use generic Bloomberg endpoints through the local gateway** - Do not create custom endpoints on the Bloomberg VM for specific features. Instead:

1. **Frontend** → **Local Gateway** (localhost:8000) → **Generic Bloomberg API**
2. Use `/api/bloomberg/reference` for all data fetching (spot, forwards, volatility, etc.)
3. Process data in the frontend component rather than expecting backend calculations
4. The local gateway (`bloomberg-gateway-enhanced.py`) proxies requests to the Bloomberg VM

Example pattern for FX Forwards:
```javascript
// DON'T create custom endpoints like /api/fx-forwards/curves
// DO use generic reference endpoint:
const securities = [
  `${pair} Curncy`,  // Spot
  `${pair}1W Curncy`, `${pair}1M Curncy`, // etc. - Forward points
]

const response = await fetch(`${apiUrl}/api/bloomberg/reference`, {
  method: 'POST',
  body: JSON.stringify({
    securities: securities,
    fields: ['PX_LAST', 'PX_BID', 'PX_ASK']
  })
})
```

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

### API Commands

```bash
# Check if API is running
curl http://20.172.249.92:8080/health

# Discover OIS tickers (OPERATIONAL)
curl -X POST "http://20.172.249.92:8080/api/bloomberg/ticker-discovery" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "ois", "currency": "USD", "max_results": 10}'

# Validate tickers with live prices (OPERATIONAL)
curl -X POST "http://20.172.249.92:8080/api/bloomberg/validate-tickers" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '["USOSFR1 Curncy", "USOSFR2 Curncy", "USOSFR5 Curncy"]'

# Reference data lookup
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

### Database Architecture (Updated 2025-08-04)
- **Single table design**: All Bloomberg tickers now in `bloomberg_tickers` table
- **Categories**: fx_spot, fx_forward, fx_vol_atm, fx_vol_rr, fx_vol_bf, ois_curve, etc.
- **FX Forwards**: Support for tenors up to 5Y (added 4Y/5Y tickers for 41 currency pairs)
- **Ticker format**: `{PAIR}{TENOR} Curncy` for forwards (e.g., EURUSD5Y Curncy)

## Recent Context (Updated 2025-01-30)

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

# Test ticker discovery (2025-01-30)
curl -X POST "http://localhost:8000/api/bloomberg/ticker-discovery" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "ois", "currency": "GBP"}'
```

## Ticker Discovery Integration (Added 2025-01-30)

### New Capabilities
Successfully deployed ticker discovery endpoints to Bloomberg VM for systematic OIS curve expansion:

### Discovery Patterns Supported
- **OIS**: USD (SOFR), EUR (ESTR), GBP (SONIA), JPY (TONA), CHF (SARON), etc.
- **IRS**: Interest Rate Swaps for major currencies
- **FX Vol**: Volatility surface tickers (ATM, RR, BF)
- **Govt Bonds**: Government bond yield curves

### Integration with Database
- **PostgreSQL**: gzc_platform.bloomberg_tickers (373 tickers, 25 currencies)
- **OIS Coverage**: USD (6 tickers), JPY (7 tickers), ready for G10 expansion
- **Dynamic Updates**: Discovery → Validation → Database population

### Usage Examples
```bash
# Discover GBP OIS tickers
curl -X POST "http://20.172.249.92:8080/api/bloomberg/ticker-discovery" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "ois", "currency": "GBP", "max_results": 50}'

# Validate discovered tickers
curl -X POST "http://20.172.249.92:8080/api/bloomberg/validate-tickers" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '["SONIOA BGN Curncy", "SONIOB BGN Curncy", "SONIOC BGN Curncy"]'
```

## FX Forward Curves Implementation (Added 2025-08-04)

### Key Implementation Details
- **Component**: `FXForwardCurvesTab.tsx` uses generic Bloomberg reference endpoint
- **Tickers**: Bloomberg provides forward points (not outright rates)
- **Calculation**: Outright rate = Spot + (Forward Points / Pip Factor)
  - USD/JPY and XXX/JPY pairs: Pip factor = 100
  - All other pairs: Pip factor = 10,000
- **Data Processing**: All calculations done in frontend component
- **Supported Tenors**: 1W, 2W, 1M, 2M, 3M, 6M, 9M, 12M, 15M, 18M, 21M, 2Y, 3Y, 4Y, 5Y

### Example Implementation
See `FXForwardCurvesTab_updated.tsx` for the correct pattern using generic endpoints.