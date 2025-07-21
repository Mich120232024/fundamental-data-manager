# BLOOMBERG GENERIC API RESEARCH
**Date**: 2025-07-16  
**Researcher**: HEAD_OF_ENGINEERING  
**Purpose**: Design generic Bloomberg API endpoint for all data types

## EXECUTIVE SUMMARY

Research confirms that a single generic Bloomberg endpoint can handle ALL data types (FX, volatility, bonds, commodities) through dynamic parameters, eliminating the need for specific endpoints.

## BLOOMBERG API ARCHITECTURE

### Core Connection Model
```
Bloomberg Terminal (Windows)
    ↓
localhost:8194 (Terminal API port)
    ↓
blpapi Session
    ↓
Services (//blp/refdata, //blp/mktdata)
```

### Security Requirement
- **CRITICAL**: API must run on SAME machine as Terminal
- No remote Bloomberg API access possible
- Terminal login session required

## GENERIC ENDPOINT DESIGN

### Single Endpoint Pattern
```python
POST /api/bloomberg/query
```

### Request Structure
```json
{
  "request_type": "ReferenceData",
  "securities": ["EURUSD Curncy", "EURUSDV1M BGN Curncy"],
  "fields": ["PX_LAST", "PX_BID", "PX_ASK"],
  "parameters": {
    "startDate": "20240101",
    "endDate": "20250716"
  },
  "overrides": {
    "SETTLE_DT": "20250716"
  }
}
```

### Request Types
1. **ReferenceData** - Current values (spot, vol, prices)
2. **HistoricalData** - Time series data
3. **IntradayTick** - Tick-by-tick data
4. **IntradayBar** - Bar data (OHLC)

## IMPLEMENTATION PATTERN

### Generic Service Class
```python
class BloombergGenericService:
    def query(self, request_type, securities, fields, **kwargs):
        """Handle all Bloomberg data requests"""
        
        if request_type == "ReferenceData":
            return self._reference_data(securities, fields, kwargs.get("overrides"))
        elif request_type == "HistoricalData":
            return self._historical_data(
                securities, fields,
                kwargs.get("start_date"),
                kwargs.get("end_date"),
                kwargs.get("periodicity", "DAILY")
            )
```

### Error Handling
```python
Bloomberg Errors Returned As-Is:
- "#N/A Limit" - Rate limit exceeded
- "#N/A Authorization" - No permission
- "#N/A Field Not Applicable" - Wrong field for security
- "#N/A Invalid Security" - Unknown ticker
- "#N/A N/A" - No data available
```

## USE CASES

### FX Spot Rates
```json
{
  "request_type": "ReferenceData",
  "securities": ["EURUSD Curncy", "GBPUSD Curncy"],
  "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
}
```

### FX Volatility Surface
```json
{
  "request_type": "ReferenceData",
  "securities": [
    "EURUSDV1M BGN Curncy",
    "EURUSD25RR1M BGN Curncy",
    "EURUSD25BF1M BGN Curncy"
  ],
  "fields": ["PX_LAST"]
}
```

### Historical Volatility
```json
{
  "request_type": "HistoricalData",
  "securities": ["EURUSDV1M BGN Curncy"],
  "fields": ["PX_LAST"],
  "parameters": {
    "startDate": "20240101",
    "endDate": "20250716",
    "periodicitySelection": "DAILY"
  }
}
```

### Commodity Prices
```json
{
  "request_type": "ReferenceData",
  "securities": ["CL1 Comdty", "GC1 Comdty"],
  "fields": ["PX_LAST", "FUT_CONT_SIZE", "OPEN_INT"]
}
```

### Bond Yields
```json
{
  "request_type": "ReferenceData",
  "securities": ["GT10 Govt", "GB10 Govt"],
  "fields": ["YLD_YTM_MID", "DUR_ADJ_MID", "PX_LAST"]
}
```

## PERFORMANCE CONSIDERATIONS

### Rate Limits
- **Daily**: 500,000 data points (security × field)
- **Monthly**: Unique securities count (varies by license)
- **Real-time**: 3,500 concurrent subscriptions

### Optimization
- Batch multiple securities in one request
- Cache static data locally
- Use appropriate request type (don't use Historical for current data)

## SECURITY PATTERNS

### Authentication
- Desktop API uses Terminal session (no extra auth)
- Request includes Bearer token for our API layer
- Bloomberg permissions apply per Terminal login

### Data Validation
- All securities validated by Bloomberg
- Invalid requests return Bloomberg errors
- No data manipulation - pure pass-through

## LOCAL TESTING APPROACH

### Simple Test Client
```python
import requests

def test_bloomberg_query(securities, fields, request_type="ReferenceData"):
    response = requests.post(
        "http://20.172.249.92:8080/api/bloomberg/query",
        headers={"Authorization": "Bearer test"},
        json={
            "request_type": request_type,
            "securities": securities,
            "fields": fields
        }
    )
    return response.json()

# Test volatility
result = test_bloomberg_query(
    ["EURUSDV1M BGN Curncy", "EURUSD25RR1M BGN Curncy"],
    ["PX_LAST"]
)
```

## IMPLEMENTATION BENEFITS

1. **Single Endpoint** - No need to update VM for new data types
2. **Dynamic Queries** - Any Bloomberg data accessible
3. **Pure Bloomberg Response** - Real data or real errors
4. **Future Proof** - Works for any new requirements
5. **Container Ready** - Same endpoint for all environments

## NEXT STEPS

1. Implement generic endpoint on VM
2. Test with volatility queries
3. Create local test client
4. Use for all Bloomberg data needs

---

**Research Sources**: Bloomberg API documentation, blpapi implementation patterns, enterprise Bloomberg architectures

—HEAD_OF_ENGINEERING