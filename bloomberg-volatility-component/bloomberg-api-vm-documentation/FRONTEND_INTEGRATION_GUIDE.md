# Frontend Integration Guide - Bloomberg Volatility Surface

## Overview
This guide documents the successful integration of a React frontend with the Bloomberg Terminal API for displaying real-time volatility surfaces. It includes critical lessons learned and solutions to common pitfalls.

## Architecture

### Backend (Working)
- **API Server**: `C:\Bloomberg\APIServer\main_checkpoint_working_2025_07_16.py`
- **Endpoint**: http://20.172.249.92:8080
- **Key Endpoint**: `/api/bloomberg/reference` (GENERIC - handles ANY Bloomberg security)

### Frontend (React + TypeScript + Vite)
- **Location**: `/gzc-volatility-surface/`
- **Port**: 3501
- **Style**: GZC Intel theme (dark professional trading interface)

## Critical Lessons Learned

### 1. The Great Endpoint Confusion
**Problem**: Multiple API files with different endpoints caused 2+ hours of debugging
- `bloomberg-api-fixed.py` - had `/api/market-data` (BROKEN)
- `main_checkpoint_working_2025_07_16.py` - has `/api/bloomberg/reference` (WORKING)
- Volatility-specific endpoints (`/api/fx/volatility/live`) - incomplete, don't use

**Solution**: ALWAYS use the generic `/api/bloomberg/reference` endpoint

### 2. The Parsing Bug That Wasted 2 Hours
**Problem**: String matching bug where `'35B1M'.includes('5B1M')` returns true
```javascript
// BAD - causes 35D data to overwrite 5D data
if (security.includes(`5B${tenor}`)) { ... }

// GOOD - uses regex to match exact pattern
const match = security.match(/(\d+)(R|B)1M/);
if (match && match[1] === '5') { ... }
```

**Lesson**: Always test parsing logic immediately. Don't make multiple changes without verifying.

### 3. Bloomberg Ticker Format Confusion
**Problem**: Documentation conflicts about ticker formats
- Documentation suggested: `EURUSD25RR1M` (double R)
- Actually works: `EURUSD25R1M` (single R)
- Same for butterflies: Use `B` not `BF`

**Solution**: Test directly with Bloomberg to verify formats

### 4. IP Whitelisting Issues
**Problem**: Azure NSG rules need updating when IP changes
- Error code 0x204 when trying to connect
- Both RDP (3389) and API (8080) ports need whitelisting

**Solution**: Update NSG rules when connection fails:
```bash
# Get current IP
curl -s https://api.ipify.org

# Update NSG rules
az network nsg rule update \
  --resource-group bloomberg-terminal-rg \
  --nsg-name bloomberg-nsg \
  --name AllowRDP \
  --source-address-prefixes YOUR_NEW_IP
```

## Available Endpoints (Often Missed)

### 1. Logs Endpoint (UNDOCUMENTED BUT USEFUL!)
```bash
GET http://20.172.249.92:8080/api/logs
```
Returns recent API logs - would have saved hours of debugging!

### 2. Health Check
```bash
GET http://20.172.249.92:8080/health
```

### 3. Generic Reference Data (THE MAIN ONE)
```bash
POST http://20.172.249.92:8080/api/bloomberg/reference
Body: {
  "securities": ["ANY_BLOOMBERG_SECURITY"],
  "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
}
```

## Frontend Implementation Details

### Component Structure
```
src/
├── api/
│   └── bloomberg.ts          # API client with CORRECT endpoint
├── components/
│   ├── Header.tsx           # Status display
│   ├── VolatilitySurfaceContainer.tsx  # Main container with currency selector
│   └── VolatilitySurfaceTable.tsx     # Table with bid/ask for all deltas
└── contexts/
    └── ThemeContext.tsx     # Dark theme matching GZC Intel
```

### Key Features Implemented
1. **Real-time Data**: No mocks, only Bloomberg Terminal data
2. **Full Bid/Ask**: Shows bid/ask for all risk reversals and butterflies
3. **Currency Selector**: 28 FX pairs in dropdown
4. **Clean Term Structure**: Only shows populated tenors
5. **Professional UI**: Dark theme with proper spacing

### Data Flow
1. User selects currency pair
2. Frontend calls `/api/bloomberg/reference` with securities list
3. API queries Bloomberg Terminal
4. Returns EXACT Bloomberg data (no transformation)
5. Frontend parses with regex to avoid substring matching bugs
6. Displays in professional volatility surface grid

## Common Pitfalls and Solutions

### 1. "Why is data missing for some deltas?"
**Cause**: Parsing bug - substring matching catches wrong securities
**Fix**: Use regex pattern matching as shown above

### 2. "API returns data but frontend shows empty"
**Cause**: Wrong API endpoint or parsing field names incorrectly
**Fix**: Use `/api/bloomberg/reference` and check exact field names

### 3. "Bloomberg Disconnected but API is running"
**Cause**: Frontend calling non-existent endpoints
**Fix**: Remove service control endpoints, use health check only

### 4. "Can't connect to VM"
**Cause**: IP not whitelisted in NSG rules
**Fix**: Update NSG rules with current IP

### 5. "Invalid security error from Bloomberg"
**Cause**: Wrong ticker format
**Fix**: Use single letters (R, B) not double (RR, BF)

## Performance Considerations
- API calls take 200-500ms per request
- Batch all tenors in single request
- No caching needed for live data
- Bloomberg Terminal must be logged in

## Security Notes
- Never hardcode credentials
- API uses simple Bearer token (configured on VM)
- NSG rules restrict access by IP
- No sensitive data in frontend code

## Testing Approach
```bash
# 1. Test API directly
curl -X POST http://20.172.249.92:8080/api/bloomberg/reference \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"securities": ["EURUSD25R1M BGN Curncy"], "fields": ["PX_LAST"]}'

# 2. Check logs if issues
curl http://20.172.249.92:8080/api/logs

# 3. Verify frontend parsing
# Add console.log statements in bloomberg.ts
```

## Deployment Notes
- Frontend runs on Vite dev server (port 3501)
- Can build for production: `npm run build`
- API must be accessible from frontend host
- CORS is configured on API server

## Maintenance
- **DO NOT MODIFY** `main_checkpoint_working_2025_07_16.py`
- Frontend can be updated freely
- Always test parsing changes immediately
- Keep NSG rules updated for active IPs

---

*Last Updated: January 20, 2025*
*Time Invested: 1 week API development + 1 day frontend (with 2+ hours wasted on bugs)*