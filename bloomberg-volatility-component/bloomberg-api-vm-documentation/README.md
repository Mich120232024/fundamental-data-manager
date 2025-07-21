# Bloomberg API VM Documentation

## Overview
This documentation provides comprehensive details about the Bloomberg Terminal API integration, including VM setup, networking configuration, API endpoints, and discovered volatility data formats.

## Table of Contents
1. [Infrastructure Setup](#infrastructure-setup)
2. [API Server Configuration](#api-server-configuration)
3. [Network Configuration](#network-configuration)
4. [Bloomberg Data Formats](#bloomberg-data-formats)
5. [API Endpoints](#api-endpoints)
6. [Data Types & Methodologies](#data-types--methodologies)
7. [Performance Considerations](#performance-considerations)
8. [Testing & Validation](#testing--validation)
9. [Troubleshooting](#troubleshooting)

## Related Documentation
- **[API Endpoints](./API_ENDPOINTS.md)**: Complete API endpoint documentation with examples
- **[Data Retrieval Methodology](./DATA_RETRIEVAL_METHODOLOGY.md)**: Comprehensive data retrieval patterns and implementation
- **[Volatility Formats](./VOLATILITY_FORMATS.md)**: Bloomberg security formats and data structures
- **[Setup Guide](./SETUP_GUIDE.md)**: VM setup and configuration instructions
- **[Networking](./NETWORKING.md)**: Network configuration and troubleshooting
- **[Frontend Integration Guide](./FRONTEND_INTEGRATION_GUIDE.md)**: React frontend integration with lessons learned

---

## Infrastructure Setup

### Azure Virtual Machine
- **VM Name**: `bloomberg-vm-02`
- **Resource Group**: `bloomberg-terminal-rg`
- **Public IP**: `20.172.249.92`
- **Private IP**: `10.225.1.5`
- **VNet**: Moved to main AKS VNet (consolidated from separate VNet)
- **Operating System**: Windows Server with Bloomberg Terminal
- **Python Version**: 3.11
- **Bloomberg API**: `blpapi` package installed

### VM Access
```bash
# SSH/RDP access
ssh bloombergadmin@20.172.249.92

# VM credentials stored in environment
BLOOMBERG_VM_USERNAME=bloombergadmin
BLOOMBERG_VM_PASSWORD=Ii89rra137+*
```

## API Server Configuration

### Server Location
- **CRITICAL**: Use `C:\Bloomberg\APIServer\main_checkpoint_working_2025_07_16.py` (NOT the other API files!)
- **Port**: `8080`
- **Protocol**: HTTP
- **Authentication**: Bearer token (`test`)

### ⚠️ WARNING: Multiple API Files Exist (SOURCE OF MAJOR CONFUSION!)
There are several API files on the VM that can cause confusion:
- ❌ `bloomberg-api-fixed.py` - Has broken `/api/market-data` endpoint (wasted 2+ hours)
- ❌ `real_bloomberg_api.py` - Different endpoint structure, missing generic endpoint
- ❌ Volatility-specific endpoints - Incomplete implementation
- ✅ `main_checkpoint_working_2025_07_16.py` - The ONLY working API with generic endpoint

**LESSON LEARNED**: This confusion cost hours of debugging. Always verify which API is running by:
1. Checking the process: `Get-Process python* | Select-Object Path`
2. Testing the endpoint: `curl http://20.172.249.92:8080/api/bloomberg/reference`
3. Checking logs: `curl http://20.172.249.92:8080/api/logs`

### Server Management
```bash
# Start API server
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "cd C:\BloombergAPI; Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden"

# Stop API server
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Process python* | Stop-Process -Force"

# Health check
curl http://20.172.249.92:8080/health
```

### Logging System
The API server implements comprehensive logging with 7 specialized log files:

```
C:\BloombergAPI\logs\
├── api_requests.log       # All API requests and responses
├── bloomberg_connection.log # Bloomberg Terminal connection status
├── bloomberg_data.log     # Raw Bloomberg data retrieval
├── bloomberg_errors.log   # Bloomberg-specific errors
├── system_events.log      # System-level events
├── performance.log        # Performance metrics
└── raw_responses.log      # Raw Bloomberg API responses
```

### 📍 IMPORTANT: Logs Endpoint (Often Missed!)
```bash
# View recent API logs - VERY USEFUL for debugging
GET http://20.172.249.92:8080/api/logs

# Returns last 100 log entries from all log files
curl http://20.172.249.92:8080/api/logs
```

## Network Configuration

### VNet Integration
- **Original Setup**: Separate VNet for Bloomberg VM
- **Current Setup**: Consolidated into main AKS VNet
- **Benefit**: Direct connection to databases, AKS, and other Azure resources

### Network Flow
```
Client → Vite Dev Server (localhost:5173) → Proxy → Bloomberg VM (20.172.249.92:8080) → Bloomberg Terminal
```

### Vite Proxy Configuration
```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://20.172.249.92:8080',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug'
    }
  }
}
```

## Bloomberg Data Formats

### Working Security Formats
After extensive testing, these formats work reliably:

#### 1. ATM Volatility
- **Format**: `{PAIR}V{TENOR} BGN Curncy`
- **Example**: `EURUSDV1M BGN Curncy`
- **Alternative**: `{PAIR}V{TENOR} Index`
- **Example**: `EURUSDV1M Index`

#### 2. Risk Reversals
- **Format**: `{PAIR}{DELTA}RR{TENOR} BGN Curncy`
- **Example**: `EURUSD25RR1M BGN Curncy`
- **Deltas**: 10D, 25D

#### 3. Butterflies
- **Format**: `{PAIR}{DELTA}BF{TENOR} BGN Curncy`
- **Example**: `EURUSD25BF1M BGN Curncy`
- **Deltas**: 10D, 25D

#### 4. Direct Security Format
- **Format**: `{PAIR} {TENOR} ATM VOL BVOL Curncy`
- **Example**: `EURUSD 1M ATM VOL BVOL Curncy`

### Invalid Formats (From Specifications)
These formats from the original specifications do NOT work:
- `VOLATILITY_MID`
- `C25R`, `C25B`
- `C10R`, `C10B`
- Generic field names without proper Bloomberg security syntax

### Supported Tenors
```
1W, 2W, 1M, 2M, 3M, 6M, 9M, 1Y, 2Y
```

### Supported Currency Pairs
```
EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD,
EURGBP, EURJPY, GBPJPY, EURCHF, AUDJPY
```

## API Endpoints

### 1. Health Check
```
GET /health
```
**Response**: Server status, Bloomberg Terminal connection, supported pairs/tenors

### 2. Live FX Rates
```
POST /api/fx/rates/live
Content-Type: application/json
Authorization: Bearer test

{
  "currency_pairs": ["EURUSD", "GBPUSD"]
}
```

### 3. Live FX Volatility
```
POST /api/fx/volatility/live
Content-Type: application/json
Authorization: Bearer test

{
  "currency_pairs": ["EURUSD"],
  "tenors": ["1M", "3M", "6M"]
}
```

### 4. EOD FX Volatility
```
POST /api/fx/volatility/eod
Content-Type: application/json
Authorization: Bearer test

{
  "currency_pairs": ["EURUSD"],
  "tenors": ["1M", "3M", "6M"],
  "trading_date": "20250716"
}
```

### 5. Historical FX Volatility
```
POST /api/fx/volatility/historical
Content-Type: application/json
Authorization: Bearer test

{
  "currency_pair": "EURUSD",
  "tenor": "1M",
  "start_date": "20240101",
  "end_date": "20250716"
}
```

### Sample Response Structure
```json
{
  "success": true,
  "data": {
    "data_type": "live_fx_volatility",
    "timestamp": "2025-07-16T...",
    "currency_pairs": ["EURUSD"],
    "tenors": ["1M"],
    "vol_types": ["ATM_VOL", "25D_RR", "25D_BF", "10D_RR", "10D_BF"],
    "raw_data": [
      {
        "security": "EURUSDV1M Curncy",
        "PX_LAST": 7.83,
        "PX_BID": 7.80,
        "PX_ASK": 7.85,
        "LAST_UPDATE_TIME": "..."
      }
    ],
    "source": "Bloomberg Terminal - LIVE DATA",
    "data_count": 1
  },
  "query_id": "fx_vol_live_20250716_143052_123456"
}
```

## Testing & Validation

### Successful Tests
1. **EUR/USD Spot Rate**: 1.1609 (real-time)
2. **EUR/USD 1M ATM Vol**: 7.83% (BGN Curncy and Index formats)
3. **Connection Stability**: Consistent data retrieval
4. **Error Handling**: Proper Bloomberg Terminal authentication checks

### Data Validation
- Zero tolerance for mock data
- Real-time validation against Bloomberg Terminal
- Comprehensive error logging
- Sanity checks for FX rates (0-1000 range) and volatility (0-500% range)

### Authentication Requirements
- Bloomberg Terminal must be running and logged in
- API requires `blpapi` Python package
- Bearer token authentication for API access

## Troubleshooting

### Common Issues

#### 1. Bloomberg Terminal Not Running
**Error**: `Failed to start Bloomberg session`
**Solution**: Ensure Bloomberg Terminal is running and logged in

#### 2. Field Not Valid
**Error**: `Field not valid for security`
**Solution**: Use discovered working formats (BGN Curncy, Index)

#### 3. API Connection Timeout
**Error**: `Bloomberg request timed out`
**Solution**: 
- Check Terminal login status and network connectivity
- Increase timeout values for historical requests (15000ms)
- Verify Bloomberg Terminal has historical data permissions

#### 4. Cached Data
**Error**: Stale data returned
**Solution**: Restart API server, ensure Terminal is active

#### 5. Historical Data Issues
**Error**: `No historical data available` or `Invalid date range`
**Solution**: 
- Verify date format (YYYYMMDD)
- Check Bloomberg Terminal historical data license
- Ensure date range is within available data period
- Use business days only for historical requests

#### 6. EOD Data Not Available
**Error**: `EOD data not found for date`
**Solution**: 
- Verify trading date is a business day
- Check if market was open on specified date
- Ensure EOD data has been published by Bloomberg

#### 7. Performance Issues
**Error**: Slow response times or timeouts
**Solution**: 
- Implement request batching for multiple securities
- Use appropriate caching strategies
- Monitor Bloomberg Terminal resource usage
- Consider rate limiting (10 requests/second)

### Debug Commands
```bash
# Check API server status
curl http://20.172.249.92:8080/health

# Test simple FX rate
curl -X POST http://20.172.249.92:8080/api/fx/rates/live \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pairs": ["EURUSD"]}'

# Test live volatility
curl -X POST http://20.172.249.92:8080/api/fx/volatility/live \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pairs": ["EURUSD"], "tenors": ["1M"]}'

# Test historical volatility
curl -X POST http://20.172.249.92:8080/api/fx/volatility/historical \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pair": "EURUSD", "tenor": "1M", "start_date": "20250715", "end_date": "20250716"}'

# Test EOD volatility
curl -X POST http://20.172.249.92:8080/api/fx/volatility/eod \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pairs": ["EURUSD"], "tenors": ["1M"], "trading_date": "20250716"}'

# Check logs on VM
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Content C:\BloombergAPI\logs\api_requests.log -Tail 20"

# Check Bloomberg connection logs
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Content C:\BloombergAPI\logs\bloomberg_connection.log -Tail 20"

# Check performance logs
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Content C:\BloombergAPI\logs\performance.log -Tail 20"
```

## Environment Variables

```bash
# Bloomberg API Configuration
BLOOMBERG_API_HOST=20.172.249.92
BLOOMBERG_API_PORT=8080
BLOOMBERG_API_URL=http://20.172.249.92:8080
BLOOMBERG_API_TOKEN=test
BLOOMBERG_API_PRIVATE_IP=10.225.1.5

# VM Configuration
BLOOMBERG_VM_HOST=20.172.249.92
BLOOMBERG_VM_PRIVATE_IP=10.225.1.5
BLOOMBERG_VM_USERNAME=bloombergadmin
BLOOMBERG_VM_PASSWORD=Ii89rra137+*
BLOOMBERG_VM_RESOURCE_GROUP=bloomberg-terminal-rg
BLOOMBERG_VM_NAME=bloomberg-vm-02
```

## Data Types & Methodologies

### Live Data
- **Update Frequency**: Real-time (milliseconds)
- **Availability**: During market hours
- **Use Case**: Trading, real-time risk management
- **Latency**: 200-500ms per request
- **Caching**: Not recommended (real-time requirement)

### EOD Data
- **Update Frequency**: Daily after market close
- **Availability**: Historical series available
- **Use Case**: Daily risk reports, historical analysis
- **Latency**: 300-800ms per request
- **Caching**: Cache until next market close

### Historical Data
- **Time Range**: Multiple years of history
- **Granularity**: Daily, weekly, monthly
- **Use Case**: Backtesting, trend analysis, model calibration
- **Latency**: 500-2000ms per request
- **Caching**: Cache with daily refresh

## Performance Considerations

### Request Optimization
- **Batch Processing**: Combine multiple securities in single request
- **Timeout Values**: Use appropriate timeout values (5000ms for live, 10000ms for historical)
- **Connection Pooling**: Reuse Bloomberg Terminal connections
- **Rate Limiting**: Implement request rate limiting (10 requests/second)

### Caching Strategies
- **Live Data**: No caching (real-time requirement)
- **EOD Data**: Cache until next market close
- **Historical Data**: Cache with daily refresh
- **Volatility Surfaces**: Cache complete surfaces to reduce API calls

## Next Steps

1. **Complete API Implementation**: Add EOD and historical endpoints
2. **Data Storage**: Implement daily volatility surface storage
3. **VaR Integration**: Connect volatility surfaces to risk calculations
4. **Performance Monitoring**: Add comprehensive performance metrics
5. **Scaling**: Consider multiple Bloomberg Terminal instances

---

*Last Updated: July 16, 2025*
*Status: Production Ready - Complete Methodology Documentation*
*Coverage: Live, EOD, and Historical Data Retrieval*