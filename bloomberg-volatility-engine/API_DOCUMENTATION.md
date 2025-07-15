# Bloomberg API Documentation

## Base URL
```
http://20.172.249.92:8080
```

## Authentication
No authentication required - API server handles Bloomberg Terminal authentication internally.

## Endpoints

### 1. Health Check
Check if the API server is running and Bloomberg is connected.

**Request:**
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-07-11T22:39:32.792143",
    "server": "Bloomberg Terminal API Server",
    "version": "3.0",
    "bloomberg_connected": true,
    "bloomberg_available": true,
    "mode": "REAL_TERMINAL"
}
```

### 2. Market Data
Get real-time market data for securities.

**Request:**
```http
POST /api/market-data
Content-Type: application/json

{
    "securities": ["AAPL US Equity", "MSFT US Equity"],
    "fields": ["PX_LAST", "CHG_PCT_1D", "VOLUME"]
}
```

**Response:**
```json
[
    {
        "security": "AAPL US Equity",
        "fields": {
            "PX_LAST": 211.16,
            "CHG_PCT_1D": -0.588,
            "VOLUME": 39726441.0
        },
        "timestamp": "2025-07-11T22:39:48.040497",
        "source": "Bloomberg Terminal"
    }
]
```

### 3. FX Rates
Get current foreign exchange rates.

**Request:**
```http
GET /api/fx/rates
```

**Response:**
```json
[
    {
        "security": "EURUSD Curncy",
        "fields": {
            "PX_LAST": 1.1689,
            "PX_BID": 1.1688,
            "PX_ASK": 1.1690,
            "CHG_PCT_1D": -0.154
        }
    }
]
```

## Security Identifiers

### Equities
- Format: `[TICKER] [EXCHANGE] Equity`
- Examples:
  - `AAPL US Equity` - Apple Inc.
  - `MSFT US Equity` - Microsoft Corp.
  - `GOOGL US Equity` - Alphabet Inc.
  - `TSLA US Equity` - Tesla Inc.

### FX
- Format: `[CCY1][CCY2] Curncy`
- Examples:
  - `EURUSD Curncy` - Euro/US Dollar
  - `GBPUSD Curncy` - British Pound/US Dollar
  - `USDJPY Curncy` - US Dollar/Japanese Yen

### Indices
- Format: `[INDEX] Index`
- Examples:
  - `SPX Index` - S&P 500
  - `INDU Index` - Dow Jones
  - `CCMP Index` - Nasdaq Composite

### Commodities
- Format: `[CONTRACT] Comdty`
- Examples:
  - `CL1 Comdty` - WTI Crude Oil
  - `GC1 Comdty` - Gold
  - `NG1 Comdty` - Natural Gas

## Available Fields

### Price Fields
- `PX_LAST` - Last Price
- `PX_BID` - Bid Price
- `PX_ASK` - Ask Price
- `PX_HIGH` - Day High
- `PX_LOW` - Day Low
- `PX_OPEN` - Open Price
- `PX_CLOSE_1D` - Previous Close

### Change Fields
- `CHG_PCT_1D` - 1-Day % Change
- `CHG_NET_1D` - 1-Day Net Change
- `CHG_PCT_WTD` - Week-to-Date % Change
- `CHG_PCT_MTD` - Month-to-Date % Change
- `CHG_PCT_YTD` - Year-to-Date % Change

### Volume Fields
- `VOLUME` - Volume
- `VOLUME_AVG_30D` - 30-Day Average Volume

### Volatility Fields (FX)
- `VOLATILITY_30D` - 30-Day Volatility
- `VOLATILITY_90D` - 90-Day Volatility

### Fundamental Fields
- `CUR_MKT_CAP` - Market Capitalization
- `PE_RATIO` - Price/Earnings Ratio
- `EQY_DVD_YLD_12M` - Dividend Yield

## Error Responses

### 503 Service Unavailable
```json
{
    "detail": "Bloomberg Terminal not connected"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Failed to get market data: [error details]"
}
```

## Example Usage

### Python
```python
import requests

# Get stock prices
response = requests.post(
    "http://20.172.249.92:8080/api/market-data",
    json={
        "securities": ["AAPL US Equity"],
        "fields": ["PX_LAST", "CHG_PCT_1D"]
    }
)
data = response.json()
print(f"Apple Price: ${data[0]['fields']['PX_LAST']}")
```

### cURL
```bash
# Get FX rates
curl http://20.172.249.92:8080/api/fx/rates

# Get stock data
curl -X POST http://20.172.249.92:8080/api/market-data \
  -H "Content-Type: application/json" \
  -d '{"securities": ["TSLA US Equity"], "fields": ["PX_LAST"]}'
```

## Rate Limits
- No explicit rate limits
- Be considerate of Bloomberg Terminal resources
- Batch requests when possible

## Notes
- All data is real-time from Bloomberg Terminal
- News API endpoints require additional Bloomberg license
- Some volatility fields may not be available depending on subscription