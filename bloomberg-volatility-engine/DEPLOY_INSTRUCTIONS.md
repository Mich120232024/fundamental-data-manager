# Bloomberg API v5.0 Deployment Instructions

## Quick Deployment Steps

### 1. Stop Current API Server
```bash
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Process python* | Stop-Process -Force -ErrorAction SilentlyContinue; Write-Host 'API server stopped'"
```

### 2. Upload New API Code
First, create a temporary file with the API code:
```bash
# Copy the API code to a temporary file
cp bloomberg_api_v5.py /tmp/bloomberg_api_temp.py
```

Then upload it to the VM:
```bash
# Use Azure CLI to copy file to VM
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/[your-repo]/bloomberg_api_v5.py' -OutFile 'C:\Bloomberg\APIServer\bloomberg_api_v5.py'"
```

**Alternative: Manual copy via Remote Desktop**
1. RDP to the VM
2. Copy the `bloomberg_api_v5.py` content
3. Save as `C:\Bloomberg\APIServer\bloomberg_api_v5.py`

### 3. Start New API Server
```bash
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "cd C:\Bloomberg\APIServer; Start-Process C:\Python311\python.exe -ArgumentList 'bloomberg_api_v5.py' -WindowStyle Hidden; Start-Sleep -Seconds 5; Get-Process python* | Select-Object Name, Id, StartTime"
```

### 4. Test New Endpoints
```bash
# Test health
curl http://20.172.249.92:8080/health

# Test volatility surface
curl http://20.172.249.92:8080/api/fx/vol-surface/EURUSD/processed

# Run comprehensive test
python3 test_api_v5.py
```

## What's New in v5.0

1. **Comprehensive Field Testing**: Tests 200+ possible volatility field names
2. **Smart Field Mapping**: Automatically tries multiple field name variations
3. **Calculated Values**: If RR/BF fields don't exist, calculates from call/put vols
4. **Bulk Data Support**: Can extract matrix/surface data if available
5. **Caching**: 60-second cache for frequently requested data
6. **Field Discovery**: New endpoint to discover available fields

## New Endpoints

- `GET /api/fx/vol-surface/<pair>` - Raw comprehensive data
- `GET /api/fx/vol-surface/<pair>/processed` - Processed with RR/BF
- `GET /api/discover/<security>` - Discover available fields
- `POST /api/market-data` - Enhanced with automatic RR/BF calculation

## Troubleshooting

If RR/BF still return empty after deployment:
1. The Bloomberg Terminal subscription may not include FX option analytics
2. The Terminal might use different field names than tested
3. Data might only be available through Terminal screens (OVDV, FXO)
4. Consider using Bloomberg Excel Add-in as alternative

## Testing After Deployment

Run the test suite:
```bash
python3 test_api_v5.py
```

This will verify:
- API is running (health check)
- Volatility surface endpoints work
- Field discovery works
- RR/BF calculation attempts

## Important Notes

- The API tries 200+ field variations to find volatility data
- If direct RR/BF fields aren't found, it attempts calculation
- All data comes from Bloomberg Terminal, not synthetic
- Performance is optimized with caching and batch requests