# Bloomberg Terminal Integration

This project provides API access to Bloomberg Terminal data running on an Azure VM.

## CRITICAL MAINTENANCE INFORMATION (Updated 2025-07-11)

### 🚨 CURRENT STATUS
- **API Server**: RUNNING on `real_bloomberg_api.py`
- **Endpoint**: http://20.172.249.92:8080
- **Bloomberg Connected**: TRUE
- **Last Verified**: 2025-07-11 22:40 UTC

### ⚡ QUICK COMMANDS
```bash
# Test if API is running
curl http://20.172.249.92:8080/health

# Get stock prices
curl -X POST http://20.172.249.92:8080/api/market-data \
  -H "Content-Type: application/json" \
  -d '{"securities": ["AAPL US Equity"], "fields": ["PX_LAST"]}'

# Get FX rates
curl http://20.172.249.92:8080/api/fx/rates
```

### 🔴 COMMON ISSUES & FIXES

1. **API Not Responding**
   - Bloomberg Terminal might be locked
   - API server stopped
   - Fix: Restart using maintenance commands below

2. **Network Changed** 
   - Update NSG rule with new IP
   - Current allowed IP: 31.217.174.203

3. **Azure Run-Command Stuck**
   - VM shows "Updating" state
   - Wait or restart VM if needed

### 🔧 MAINTENANCE COMMANDS
```bash
# Restart API server
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Process python* | Stop-Process -Force -ErrorAction SilentlyContinue; cd C:\Bloomberg\APIServer; Start-Process C:\Python311\python.exe -ArgumentList 'real_bloomberg_api.py' -WindowStyle Hidden"

# Check what's running
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Process python* | Select-Object Name, Id, StartTime"

# Update NSG for new IP
CURRENT_IP=$(curl -s https://api.ipify.org)
az network nsg rule update -g bloomberg-terminal-rg --nsg-name bloomberg-nsg \
  -n AllowRDP --source-address-prefixes "$CURRENT_IP"
```

### 📊 AVAILABLE DATA

#### Working Fields
- **Equities**: PX_LAST, CHG_PCT_1D, VOLUME, PX_BID, PX_ASK, PE_RATIO
- **FX**: PX_LAST, VOLATILITY_30D, VOLATILITY_90D, CHG_PCT_1D
- **Indices**: All standard price fields

#### NOT Available
- News content (requires separate license)
- Some implied volatility fields
- Options chains

### 🔐 SECURITY NOTES
- Never expose credentials in code
- API server uses Windows auth to Bloomberg
- Keep NSG rules restrictive

### 📁 KEY FILES
- **Main Server**: C:\Bloomberg\APIServer\real_bloomberg_api.py
- **Client Library**: bloomberg_client.py
- **Maintenance Log**: MAINTENANCE_LOG.md

### ⚠️ CRITICAL REMINDERS
1. Bloomberg Terminal must be logged in
2. API does NOT auto-start on reboot
3. Check health endpoint first before debugging
4. Real data only - no mocks!