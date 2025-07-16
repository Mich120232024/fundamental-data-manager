# Bloomberg API Endpoints Documentation

## Base Configuration
- **Base URL**: `http://20.172.249.92:8080`
- **Authentication**: Bearer Token
- **Token**: `test`
- **Content-Type**: `application/json`

## Related Documentation
- **[README](./README.md)**: Complete system overview and setup
- **[Data Retrieval Methodology](./DATA_RETRIEVAL_METHODOLOGY.md)**: Implementation patterns and data validation
- **[Volatility Formats](./VOLATILITY_FORMATS.md)**: Bloomberg security formats and examples
- **[Setup Guide](./SETUP_GUIDE.md)**: VM configuration and testing procedures
- **[Networking](./NETWORKING.md)**: Network configuration and performance optimization

## Endpoints Overview

### 1. Health Check
### 2. Live FX Rates
### 3. Live FX Volatility
### 4. EOD FX Volatility
### 5. Historical FX Volatility

---

## 1. Health Check

### Endpoint
```
GET /health
```

### Description
Comprehensive health check that validates Bloomberg Terminal connection and returns system status.

### Headers
None required

### Response
```json
{
  "success": true,
  "data": {
    "api_status": "healthy",
    "bloomberg_api_available": true,
    "bloomberg_terminal_running": true,
    "bloomberg_service_available": true,
    "bloomberg_error": null,
    "supported_fx_pairs": [
      "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
      "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "AUDJPY"
    ],
    "supported_tenors": [
      "O/N", "T/N", "1W", "2W", "3W", "1M", "2M", "3M", "4M", "5M", "6M", "9M", "1Y", "18M", "2Y", "3Y", "5Y"
    ],
    "server_time": "2025-07-16T14:30:00.000Z",
    "is_using_mock_data": false
  },
  "error": null,
  "timestamp": "2025-07-16T14:30:00.000Z",
  "query_id": "health_20250716_143000_123456"
}
```

### Error Response
```json
{
  "success": true,
  "data": {
    "api_status": "healthy",
    "bloomberg_api_available": false,
    "bloomberg_terminal_running": false,
    "bloomberg_service_available": false,
    "bloomberg_error": "Bloomberg API (blpapi) not installed"
  },
  "error": "Bloomberg API (blpapi) not installed",
  "timestamp": "2025-07-16T14:30:00.000Z"
}
```

### cURL Example
```bash
curl -X GET http://20.172.249.92:8080/health
```

---

## 2. Live FX Rates

### Endpoint
```
POST /api/fx/rates/live
```

### Description
Retrieves real-time FX rates from Bloomberg Terminal for specified currency pairs.

### Headers
```
Content-Type: application/json
Authorization: Bearer test
```

### Request Body
```json
{
  "currency_pairs": ["EURUSD", "GBPUSD", "USDJPY"]
}
```

### Request Parameters
- `currency_pairs` (required): Array of currency pair strings
  - Valid pairs: `EURUSD`, `GBPUSD`, `USDJPY`, `USDCHF`, `AUDUSD`, `USDCAD`, `NZDUSD`, `EURGBP`, `EURJPY`, `GBPJPY`, `EURCHF`, `AUDJPY`

### Response
```json
{
  "success": true,
  "data": {
    "data_type": "live_fx_rates",
    "timestamp": "2025-07-16T14:30:00.000Z",
    "currency_pairs": ["EURUSD", "GBPUSD"],
    "rate_types": ["SPOT", "BID", "ASK", "OPEN", "HIGH", "LOW"],
    "raw_data": [
      {
        "security": "EURUSD Curncy",
        "currency_pair": "EURUSD",
        "PX_LAST": 1.1609,
        "PX_BID": 1.1608,
        "PX_ASK": 1.1610,
        "PX_OPEN": 1.1605,
        "PX_HIGH": 1.1615,
        "PX_LOW": 1.1600,
        "LAST_UPDATE_TIME": "2025-07-16T14:29:45"
      },
      {
        "security": "GBPUSD Curncy",
        "currency_pair": "GBPUSD",
        "PX_LAST": 1.2945,
        "PX_BID": 1.2944,
        "PX_ASK": 1.2946,
        "PX_OPEN": 1.2940,
        "PX_HIGH": 1.2950,
        "PX_LOW": 1.2935,
        "LAST_UPDATE_TIME": "2025-07-16T14:29:45"
      }
    ],
    "source": "Bloomberg Terminal - LIVE DATA",
    "data_count": 2
  },
  "error": null,
  "timestamp": "2025-07-16T14:30:00.000Z",
  "query_id": "fx_rates_live_20250716_143000_123456"
}
```

### Error Response
```json
{
  "detail": "Bloomberg Terminal not available: Failed to start Bloomberg session"
}
```

### cURL Example
```bash
curl -X POST http://20.172.249.92:8080/api/fx/rates/live \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{
    "currency_pairs": ["EURUSD", "GBPUSD"]
  }'
```

---

## 3. Live FX Volatility

### Endpoint
```
POST /api/fx/volatility/live
```

### Description
Retrieves real-time FX volatility surface data from Bloomberg Terminal, including ATM volatility, Risk Reversals, and Butterflies for specified currency pairs and tenors.

### Headers
```
Content-Type: application/json
Authorization: Bearer test
```

### Request Body
```json
{
  "currency_pairs": ["EURUSD", "GBPUSD"],
  "tenors": ["1W", "1M", "3M", "6M", "1Y"]
}
```

### Request Parameters
- `currency_pairs` (required): Array of currency pair strings
  - Valid pairs: `EURUSD`, `GBPUSD`, `USDJPY`, `USDCHF`, `AUDUSD`, `USDCAD`, `NZDUSD`, `EURGBP`, `EURJPY`, `GBPJPY`, `EURCHF`, `AUDJPY`
- `tenors` (required): Array of tenor strings
  - Valid tenors: `O/N`, `T/N`, `1W`, `2W`, `3W`, `1M`, `2M`, `3M`, `4M`, `5M`, `6M`, `9M`, `1Y`, `18M`, `2Y`, `3Y`, `5Y`

### Response
```json
{
  "success": true,
  "data": {
    "data_type": "live_fx_volatility",
    "timestamp": "2025-07-16T14:30:00.000Z",
    "currency_pairs": ["EURUSD"],
    "tenors": ["1M"],
    "vol_types": ["ATM_VOL", "25D_RR", "25D_BF", "10D_RR", "10D_BF"],
    "raw_data": [
      {
        "security": "EURUSDV1M Curncy",
        "PX_LAST": 7.83,
        "PX_BID": 7.80,
        "PX_ASK": 7.85,
        "LAST_UPDATE_TIME": "2025-07-16T14:29:45"
      },
      {
        "security": "EURUSD25RR1M Curncy",
        "PX_LAST": -0.45,
        "PX_BID": -0.50,
        "PX_ASK": -0.40,
        "LAST_UPDATE_TIME": "2025-07-16T14:29:45"
      },
      {
        "security": "EURUSD25BF1M Curncy",
        "PX_LAST": 0.23,
        "PX_BID": 0.20,
        "PX_ASK": 0.25,
        "LAST_UPDATE_TIME": "2025-07-16T14:29:45"
      },
      {
        "security": "EURUSD10RR1M Curncy",
        "PX_LAST": -0.15,
        "PX_BID": -0.18,
        "PX_ASK": -0.12,
        "LAST_UPDATE_TIME": "2025-07-16T14:29:45"
      },
      {
        "security": "EURUSD10BF1M Curncy",
        "PX_LAST": 0.08,
        "PX_BID": 0.06,
        "PX_ASK": 0.10,
        "LAST_UPDATE_TIME": "2025-07-16T14:29:45"
      }
    ],
    "source": "Bloomberg Terminal - LIVE DATA",
    "data_count": 5
  },
  "error": null,
  "timestamp": "2025-07-16T14:30:00.000Z",
  "query_id": "fx_vol_live_20250716_143000_123456"
}
```

### Volatility Surface Structure
For each currency pair and tenor combination, the API returns:
- **ATM Volatility**: `{PAIR}V{TENOR} Curncy`
- **25D Risk Reversal**: `{PAIR}25RR{TENOR} Curncy`
- **25D Butterfly**: `{PAIR}25BF{TENOR} Curncy`
- **10D Risk Reversal**: `{PAIR}10RR{TENOR} Curncy`
- **10D Butterfly**: `{PAIR}10BF{TENOR} Curncy`

### Error Response
```json
{
  "detail": "Bloomberg Terminal not available: Failed to start Bloomberg session"
}
```

### cURL Example
```bash
curl -X POST http://20.172.249.92:8080/api/fx/volatility/live \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{
    "currency_pairs": ["EURUSD"],
    "tenors": ["1M", "3M", "6M"]
  }'
```

---

## 4. EOD FX Volatility

### Endpoint
```
POST /api/fx/volatility/eod
```

### Description
Retrieves end-of-day FX volatility surface data from Bloomberg Terminal for specified currency pairs, tenors, and trading date.

### Headers
```
Content-Type: application/json
Authorization: Bearer test
```

### Request Body
```json
{
  "currency_pairs": ["EURUSD", "GBPUSD"],
  "tenors": ["1W", "1M", "3M", "6M", "1Y"],
  "trading_date": "20250716"
}
```

### Request Parameters
- `currency_pairs` (required): Array of currency pair strings
- `tenors` (required): Array of tenor strings
- `trading_date` (optional): Specific trading date in YYYYMMDD format

### Response
```json
{
  "success": true,
  "data": {
    "data_type": "eod_fx_volatility",
    "timestamp": "2025-07-16T18:00:00.000Z",
    "trading_date": "20250716",
    "currency_pairs": ["EURUSD"],
    "tenors": ["1M"],
    "vol_types": ["ATM_VOL", "25D_RR", "25D_BF", "10D_RR", "10D_BF"],
    "raw_data": [
      {
        "security": "EURUSDV1M Curncy",
        "PX_LAST": 7.85,
        "PX_OPEN": 7.80,
        "PX_HIGH": 7.90,
        "PX_LOW": 7.75,
        "PX_VOLUME": 1250000,
        "TRADING_DATE": "2025-07-16"
      }
    ],
    "source": "Bloomberg Terminal - EOD DATA",
    "data_count": 1
  },
  "error": null,
  "timestamp": "2025-07-16T18:00:00.000Z",
  "query_id": "fx_vol_eod_20250716_180000_123456"
}
```

### cURL Example
```bash
curl -X POST http://20.172.249.92:8080/api/fx/volatility/eod \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{
    "currency_pairs": ["EURUSD"],
    "tenors": ["1M", "3M"],
    "trading_date": "20250716"
  }'
```

---

## 5. Historical FX Volatility

### Endpoint
```
POST /api/fx/volatility/historical
```

### Description
Retrieves historical FX volatility time series data from Bloomberg Terminal for specified currency pair, tenor, and date range.

### Headers
```
Content-Type: application/json
Authorization: Bearer test
```

### Request Body
```json
{
  "currency_pair": "EURUSD",
  "tenor": "1M",
  "start_date": "20240101",
  "end_date": "20250716",
  "periodicity": "DAILY"
}
```

### Request Parameters
- `currency_pair` (required): Single currency pair string
- `tenor` (required): Single tenor string
- `start_date` (required): Start date in YYYYMMDD format
- `end_date` (required): End date in YYYYMMDD format
- `periodicity` (optional): "DAILY", "WEEKLY", "MONTHLY" (default: "DAILY")

### Response
```json
{
  "success": true,
  "data": {
    "data_type": "historical_fx_volatility",
    "timestamp": "2025-07-16T14:30:00.000Z",
    "currency_pair": "EURUSD",
    "tenor": "1M",
    "date_range": {
      "start": "20240101",
      "end": "20250716"
    },
    "periodicity": "DAILY",
    "time_series": [
      {
        "date": "2024-01-01",
        "volatility": 7.65,
        "volume": 1150000
      },
      {
        "date": "2024-01-02",
        "volatility": 7.70,
        "volume": 1200000
      }
    ],
    "source": "Bloomberg Terminal - HISTORICAL DATA",
    "data_count": 365
  },
  "error": null,
  "timestamp": "2025-07-16T14:30:00.000Z",
  "query_id": "fx_vol_hist_20250716_143000_123456"
}
```

### Historical Data Fields
- `date` - Trading date
- `volatility` - ATM volatility level
- `volume` - Trading volume (if available)

### cURL Example
```bash
curl -X POST http://20.172.249.92:8080/api/fx/volatility/historical \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{
    "currency_pair": "EURUSD",
    "tenor": "1M",
    "start_date": "20240101",
    "end_date": "20250716"
  }'
```

---

## Authentication

### Bearer Token
All API endpoints (except health check) require Bearer token authentication:
```
Authorization: Bearer test
```

### Error Response for Invalid Token
```json
{
  "detail": "Invalid API key"
}
```

## Rate Limiting

Currently no rate limiting implemented. Bloomberg Terminal API has natural rate limits based on:
- Terminal connection capacity
- Data subscription limits
- Request processing time

## Error Handling

### Common HTTP Status Codes
- `200` - Success
- `401` - Unauthorized (invalid API key)
- `422` - Validation Error (invalid parameters)
- `500` - Internal Server Error (Bloomberg connection issues)
- `503` - Service Unavailable (Bloomberg Terminal not running)

### Error Response Format
```json
{
  "detail": "Error message describing the issue"
}
```

## Response Headers

### Standard Headers
- `Content-Type: application/json`
- `Server: uvicorn`

### Custom Headers
- `X-Query-ID` - Unique query identifier for tracking
- `X-Data-Source` - Always "Bloomberg Terminal"
- `X-Mock-Data` - Always "false"

## Testing Endpoints

### Development Environment
```bash
# Local development with proxy
curl -X GET http://localhost:5173/api/health

# Direct VM access
curl -X GET http://20.172.249.92:8080/health
```

### Production Environment
```bash
# Production API endpoint
curl -X GET http://20.172.249.92:8080/health
```

## WebSocket Support

Currently not implemented. All endpoints are REST-based with request/response pattern.

### Future WebSocket Implementation
- Real-time volatility streaming
- Live quote updates
- Market event notifications

## Performance Metrics

### Typical Response Times
- Health check: 50-100ms
- FX rates (single pair): 200-500ms
- FX rates (multiple pairs): 300-800ms
- Live volatility surface (single tenor): 500-1000ms
- Live volatility surface (multiple tenors): 1000-3000ms
- EOD volatility surface: 800-2000ms
- Historical volatility (1 year): 2000-5000ms
- Historical volatility (batch): 5000-15000ms

### Optimization Recommendations
1. **Batch requests** when possible to reduce API calls
2. **Cache strategically**:
   - Live data: No caching (real-time requirement)
   - EOD data: Cache until next market close
   - Historical data: Cache with daily refresh
3. **Implement request debouncing** on client-side
4. **Use appropriate timeouts**:
   - Live data: 5000ms
   - EOD data: 8000ms
   - Historical data: 15000ms
5. **Rate limiting**: Implement 10 requests/second limit
6. **WebSocket implementation** for real-time updates (future)

### Data Type Considerations
- **Live Data**: Use for real-time trading and risk management
- **EOD Data**: Use for daily reports and overnight risk calculations
- **Historical Data**: Use for backtesting and model calibration
- **Batch Processing**: Use for initial data loading and bulk operations

---

*Last Updated: July 16, 2025*
*Status: Production Ready - Complete API Documentation*
*Coverage: Live, EOD, and Historical Endpoints*