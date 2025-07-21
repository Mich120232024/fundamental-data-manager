# Bloomberg API Working Checkpoint - July 16, 2025

## Overview
This checkpoint documents the current working state of the Bloomberg FX Volatility API as of July 16, 2025. The API is functioning correctly with all deltas and tenors returning real Bloomberg Terminal data.

## Server Details
- **Location**: C:\BloombergAPI\main.py on bloomberg-vm-02
- **Backup Created**: C:\BloombergAPI\main_backup_2025_07_16.py
- **Endpoint**: http://20.172.249.92:8080
- **Port**: 8080
- **Authentication**: Bearer token "test"

## Working Endpoints

### 1. Health Check
```bash
GET /health
```
Returns server status and Bloomberg connection state.

### 2. FX Rates (Live)
```bash
POST /api/fx/rates/live
Authorization: Bearer test
Content-Type: application/json

{
    "currency_pairs": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF"]
}
```

### 3. FX Volatility
```bash
POST /api/fx/volatility
Authorization: Bearer test
Content-Type: application/json

{
    "currency_pairs": ["EURUSD", "GBPUSD", "USDJPY"],
    "tenors": ["1W", "1M", "3M", "6M", "1Y"]
}
```

### 4. Bloomberg Reference Data (Generic)
```bash
POST /api/bloomberg/reference
Authorization: Bearer test
Content-Type: application/json

{
    "securities": ["EURUSD Curncy", "GBPUSD Curncy"],
    "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
}
```

## Bloomberg Ticker Formats

### Currency Pairs
- Format: `{PAIR} Curncy`
- Examples: `EURUSD Curncy`, `GBPUSD Curncy`, `USDJPY Curncy`

### FX Volatility
- Format: `{PAIR}{DELTA}{TENOR} Curncy`
- Delta Codes:
  - 25D = 25 Delta
  - 10D = 10 Delta
  - ATM = At The Money
  - 25C = 25 Call
  - 10C = 10 Call
- Tenor Codes:
  - 1W = 1 Week
  - 1M = 1 Month
  - 3M = 3 Months
  - 6M = 6 Months
  - 1Y = 1 Year
- Examples:
  - `EURUSD25D1M Curncy` - EUR/USD 25 Delta 1 Month
  - `GBPUSDATM3M Curncy` - GBP/USD At The Money 3 Months
  - `USDJPY10C1Y Curncy` - USD/JPY 10 Call 1 Year

## Working Field Names
- `PX_LAST` - Last price
- `PX_BID` - Bid price
- `PX_ASK` - Ask price
- `PX_OPEN` - Open price
- `PX_HIGH` - High price
- `PX_LOW` - Low price
- `VOLATILITY_90D` - 90-day volatility (for volatility queries)

## Example Responses

### FX Rates Response
```json
{
    "success": true,
    "data": {
        "data_type": "live_fx_rates",
        "timestamp": "2025-07-16T10:30:45.123456",
        "currency_pairs": ["EURUSD", "GBPUSD"],
        "rate_types": ["SPOT", "BID", "ASK", "OPEN", "HIGH", "LOW"],
        "raw_data": [
            {
                "security": "EURUSD Curncy",
                "currency_pair": "EURUSD",
                "PX_LAST": 1.0856,
                "PX_BID": 1.0855,
                "PX_ASK": 1.0857,
                "PX_OPEN": 1.0850,
                "PX_HIGH": 1.0862,
                "PX_LOW": 1.0848,
                "LAST_UPDATE_TIME": "2025-07-16T10:30:45.123456"
            }
        ],
        "source": "Bloomberg Terminal - LIVE DATA",
        "data_count": 2
    },
    "error": null,
    "timestamp": "2025-07-16T10:30:45.123456",
    "query_id": "fx_rates_live_20250716_103045_123456"
}
```

### FX Volatility Response
```json
{
    "success": true,
    "data": {
        "data_type": "fx_implied_volatility",
        "timestamp": "2025-07-16T10:30:45.123456",
        "volatility_surface": [
            {
                "currency_pair": "EURUSD",
                "delta": "25D",
                "tenor": "1M",
                "ticker": "EURUSD25D1M Curncy",
                "volatility": 7.825,
                "success": true
            },
            {
                "currency_pair": "EURUSD",
                "delta": "ATM",
                "tenor": "1M",
                "ticker": "EURUSDATM1M Curncy",
                "volatility": 7.650,
                "success": true
            }
        ],
        "source": "Bloomberg Terminal - REAL DATA",
        "total_points": 15,
        "successful_points": 15,
        "is_using_mock_data": false
    },
    "error": null,
    "timestamp": "2025-07-16T10:30:45.123456",
    "query_id": "fx_vol_20250716_103045_123456"
}
```

## Test Results Summary

All volatility combinations tested and working:
- **Currency Pairs**: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD, USDCHF
- **Deltas**: 25D, 10D, ATM, 25C, 10C
- **Tenors**: 1W, 1M, 3M, 6M, 1Y

Total combinations: 7 pairs × 5 deltas × 5 tenors = 175 volatility points
All 175 points returning real Bloomberg data successfully.

## Critical Implementation Details

1. **Bloomberg Connection**:
   - Uses `blpapi` Python package
   - Connects to localhost:8194 (Bloomberg Terminal API port)
   - Uses "//blp/refdata" service for reference data

2. **Error Handling**:
   - Returns HTTP 503 if Bloomberg Terminal not available
   - Logs all requests with unique query IDs
   - Never returns mock data - fails explicitly if no real data

3. **Security**:
   - Bearer token authentication required
   - CORS enabled for all origins
   - All requests logged to C:/BloombergAPI/logs/api_requests.log

4. **FastAPI Server**:
   - Runs on all interfaces (0.0.0.0)
   - Port 8080
   - Logging level: INFO
   - Access logs enabled

## Maintenance Commands

### Check API Status
```bash
curl http://20.172.249.92:8080/health
```

### Restart API Server
```bash
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Process python* | Stop-Process -Force; cd C:\BloombergAPI; Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden"
```

### View API Logs
```bash
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Content C:\BloombergAPI\logs\api_requests.log -Tail 50"
```

## Notes
- This is the production-ready version with zero tolerance for mock data
- All data comes directly from Bloomberg Terminal
- The API will fail gracefully if Bloomberg Terminal is not available
- Backup created on VM at: C:\BloombergAPI\main_backup_2025_07_16.py