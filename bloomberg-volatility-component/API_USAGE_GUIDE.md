# Bloomberg API Usage Guide

## Current Working API

**File**: `C:\Bloomberg\APIServer\main_checkpoint_working_2025_07_16.py`  
**Endpoint**: http://20.172.249.92:8080  
**Status**: ✅ PRODUCTION READY - DO NOT MODIFY

## Available Endpoints

### 1. Health Check
```bash
GET http://20.172.249.92:8080/health
```

Response:
```json
{
  "success": true,
  "data": {
    "api_status": "healthy",
    "bloomberg_terminal_running": true,
    "bloomberg_service_available": true
  }
}
```

### 2. Generic Bloomberg Reference Data (MAIN ENDPOINT)
```bash
POST http://20.172.249.92:8080/api/bloomberg/reference
Headers:
  Content-Type: application/json
  Authorization: Bearer test

Body:
{
  "securities": ["EURUSD25R1M BGN Curncy", "EURUSDV1M BGN Curncy"],
  "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
}
```

This endpoint can handle ANY Bloomberg security - stocks, FX, volatilities, bonds, etc.

## Volatility Surface Securities Format

### ATM Volatility
- Format: `{PAIR}V{TENOR} BGN Curncy`
- Example: `EURUSDV1M BGN Curncy`

### Risk Reversals (Single R, not RR!)
- Format: `{PAIR}{DELTA}R{TENOR} BGN Curncy`
- Example: `EURUSD25R1M BGN Curncy`
- Valid deltas: 5, 10, 15, 25, 35

### Butterflies (Single B, not BF!)
- Format: `{PAIR}{DELTA}B{TENOR} BGN Curncy`
- Example: `EURUSD25B1M BGN Curncy`
- Valid deltas: 5, 10, 15, 25, 35

## Example: Get Full Volatility Surface

```bash
curl -X POST http://20.172.249.92:8080/api/bloomberg/reference \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{
    "securities": [
      "EURUSDV1M BGN Curncy",
      "EURUSD5R1M BGN Curncy",
      "EURUSD5B1M BGN Curncy",
      "EURUSD10R1M BGN Curncy",
      "EURUSD10B1M BGN Curncy",
      "EURUSD15R1M BGN Curncy",
      "EURUSD15B1M BGN Curncy",
      "EURUSD25R1M BGN Curncy",
      "EURUSD25B1M BGN Curncy",
      "EURUSD35R1M BGN Curncy",
      "EURUSD35B1M BGN Curncy"
    ],
    "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
  }'
```

## Important Notes

1. **DO NOT USE** the volatility-specific endpoints like `/api/fx/volatility/live` - they are incomplete
2. **ALWAYS USE** the generic `/api/bloomberg/reference` endpoint
3. **NEVER MODIFY** the working API file - it took a week to get it working perfectly
4. The API returns data in the order Bloomberg provides it (may not match request order)
5. Single letter format: Use `R` for risk reversals, `B` for butterflies (not `RR` or `BF`)

## Checking API Status

```bash
# Check if API is running
curl http://20.172.249.92:8080/health

# Test with a simple security
curl -X POST http://20.172.249.92:8080/api/bloomberg/reference \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"securities": ["EURUSD Curncy"], "fields": ["PX_LAST"]}'
```

## VM Access
- IP: 20.172.249.92
- Port: 8080 (API)
- Port: 3389 (RDP)
- API File Location: `C:\Bloomberg\APIServer\main_checkpoint_working_2025_07_16.py`

## Remember
- This API is generic and works with ANY Bloomberg security
- The terminal must be logged in for the API to work
- All data comes from real Bloomberg Terminal - no mocks
- The API was professionally built and tested - trust it