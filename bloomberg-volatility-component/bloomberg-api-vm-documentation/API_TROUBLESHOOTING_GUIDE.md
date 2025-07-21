# Bloomberg API Troubleshooting Guide

## Common Issues and Solutions

### 1. API Authentication Errors

**Symptom**: `{"detail":"Not authenticated"}`

**Solution**: 
- Use Bearer token authentication: `Authorization: Bearer test`
- NOT `X-API-Key` header alone

**Example**:
```bash
curl -X POST http://20.172.249.92:8080/api/bloomberg/reference \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"securities": ["EURUSD25R1M BGN Curncy"], "fields": ["PX_LAST"]}'
```

### 2. Wrong API Running

**Symptom**: 404 errors on `/api/bloomberg/reference`

**Solution**: 
- Check which Python script is running
- Correct file: `main_checkpoint_working_2025_07_16.py`
- Wrong files: `real_bloomberg_api.py`, others with `/api/market-data`

**To restart correct API**:
```bash
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Process python* | Stop-Process -Force; cd C:\Bloomberg\APIServer; Start-Process python.exe -ArgumentList 'main_checkpoint_working_2025_07_16.py' -WindowStyle Hidden"
```

### 3. IP Access Denied (Error 0x204)

**Symptom**: Cannot connect to VM or API

**Solution**: Update Azure NSG rules with your current IP
```bash
# Get your current IP
curl ifconfig.me

# Update NSG rules for both RDP (3389) and API (8080)
```

### 4. Ticker Returns "Unknown/Invalid Security"

**Common Causes**:
1. Incorrect ticker format
2. Missing Bloomberg data subscription
3. Ticker doesn't exist

**Debugging Steps**:
```bash
# Test known working ticker first
curl -X POST http://20.172.249.92:8080/api/bloomberg/reference \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"securities": ["EURUSD25R1M BGN Curncy"], "fields": ["PX_LAST"]}'

# Then test problematic ticker
# Check exact error message in response
```

### 5. Data Not Updating with Date Selection

**Symptom**: Historical data shows same values regardless of date

**Solution**: 
- Ensure date format is YYYYMMDD (no hyphens)
- Check if market was open on selected date
- Verify historical endpoint is working

**Test Historical Data**:
```bash
curl -X POST http://20.172.249.92:8080/api/bloomberg/historical \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{
    "security": "EURUSD25R1M BGN Curncy",
    "fields": ["PX_LAST", "PX_BID", "PX_ASK"],
    "start_date": "20250120",
    "end_date": "20250120",
    "periodicity": "DAILY"
  }'
```

### 6. Parsing Issues (Wrong Delta Showing)

**Symptom**: 35D data showing in 5D column

**Cause**: Substring matching bug (`"35B1M".includes("5B1M")` returns true)

**Solution**: Use regex matching instead:
```javascript
// Wrong
if (security.includes('5B1M'))

// Correct
const match = security.match(/EURUSD(\d+)(R|B)1M\s+BGN/)
if (match && match[1] === '5')
```

### 7. Empty Rows in Table

**Symptom**: Rows with all "-" values

**Solution**: Filter out empty tenors:
```javascript
const filteredData = surfaceData.filter(row => {
  return row.atm_bid !== null || row.atm_ask !== null || 
         row.rr_25d_bid !== null || row.rr_25d_ask !== null
  // ... check all fields
})
```

### 8. ON (Overnight) Data Not Showing

**Cause**: ON uses different ticker format

**Solution**: 
- ATM: `EURUSDVON Curncy` (no BGN)
- RR/BF: `EURUSD25RON BGN Curncy` (with BGN)

### 9. 1D/2D/3D Tickers Not Working

**Finding**: These tickers don't exist in standard Bloomberg FX options data

**Tested formats that failed**:
- `EUR1D25R BGN Curncy`
- `EURUSDV1D BGN Curncy`
- `EURUSD1D25R BGN Curncy`

**Note**: `EURUSD1D BGN Curncy` returns FX forward data, not volatility

## Debugging Tools

### Check API Health
```bash
curl http://20.172.249.92:8080/health
```

### View API Logs
```bash
curl http://20.172.249.92:8080/api/logs -H "Authorization: Bearer test"
```

### Test Specific Ticker
```python
# Use test_bloomberg_tickers.py script
python3 test_tickers_via_api.py
```

## Quick Fixes

1. **Restart API**: Use Azure CLI command above
2. **Clear Browser Cache**: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
3. **Check Console**: F12 → Console tab for detailed errors
4. **Verify Network**: F12 → Network tab to see API calls