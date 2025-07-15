# Bloomberg API Configuration Reference

## Current Working Configuration

### API Server Details
- **Server**: `real_bloomberg_api.py`
- **Location**: `C:\Bloomberg\APIServer\real_bloomberg_api.py`
- **Endpoint**: `http://20.172.249.92:8080`
- **Status**: Running on bloomberg-vm-02

### Available Endpoints
1. **Health Check**: `GET /health`
2. **Market Data**: `POST /api/market-data`
3. **FX Rates**: `GET /api/fx/rates`

### React App Configuration

#### Vite Proxy (vite.config.ts)
```typescript
proxy: {
  '/api': {
    target: 'http://20.172.249.92:8080',
    changeOrigin: true,
    secure: false,
  },
  '/health': {
    target: 'http://20.172.249.92:8080',
    changeOrigin: true,
    secure: false,
  },
}
```

#### Bloomberg Service (src/services/bloomberg.ts)
```typescript
const USE_MOCK_DATA = false; // Change to false for real data
const BLOOMBERG_API_URL = ''; // Empty because using Vite proxy
```

### Volatility Surface Securities

#### ATM Volatilities
- `EURUSDV1M Curncy` - 1 month
- `EURUSDV2M Curncy` - 2 month
- `EURUSDV3M Curncy` - 3 month
- `EURUSDV6M Curncy` - 6 month
- `EURUSDV1Y Curncy` - 1 year

#### Risk Reversals (25 Delta)
- `EUR25R1M Curncy` - 1 month
- `EUR25R2M Curncy` - 2 month
- `EUR25R3M Curncy` - 3 month
- `EUR25R6M Curncy` - 6 month
- `EUR25R1Y Curncy` - 1 year

#### Butterflies (25 Delta)
- `EUR25B1M Curncy` - 1 month
- `EUR25B2M Curncy` - 2 month
- `EUR25B3M Curncy` - 3 month
- `EUR25B6M Curncy` - 6 month
- `EUR25B1Y Curncy` - 1 year

### Testing Commands

```bash
# Test from local machine
curl http://20.172.249.92:8080/health

# Get FX volatility data
curl -X POST http://20.172.249.92:8080/api/market-data \
  -H "Content-Type: application/json" \
  -d '{
    "securities": ["EURUSDV1M Curncy", "EUR25R1M Curncy", "EUR25B1M Curncy"],
    "fields": ["PX_LAST"]
  }'
```

### Archive Information
- Old API files archived to: `C:\Bloomberg\APIServer\archive_20250714_054451\`
- Only keeping: `real_bloomberg_api.py` (the working version)

—SOFTWARE_RESEARCH_ANALYST