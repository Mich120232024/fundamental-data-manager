# Bloomberg API Server Maintenance Log

## Current Status (2025-07-11)

### ✅ API Server Status
- **Server**: Running on `real_bloomberg_api.py`
- **URL**: http://20.172.249.92:8080
- **Health Check**: http://20.172.249.92:8080/health
- **Bloomberg Connected**: TRUE
- **Version**: 3.0

### 🔧 Server Details
- **VM Name**: bloomberg-vm-02
- **Resource Group**: bloomberg-terminal-rg
- **Location**: West Europe
- **Public IP**: 20.172.249.92
- **Private IP**: 10.225.1.5
- **OS**: Windows Server 2022
- **Python**: C:\Python311\python.exe
- **Bloomberg API**: C:\blp\API\Python

### 📡 Working Endpoints

#### 1. Health Check
```bash
GET /health
GET /api/health
```
Returns:
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

#### 2. Market Data
```bash
POST /api/market-data
```
Body:
```json
{
    "securities": ["AAPL US Equity", "MSFT US Equity"],
    "fields": ["PX_LAST", "CHG_PCT_1D", "VOLUME"]
}
```

#### 3. FX Rates
```bash
GET /api/fx/rates
```

### 📊 Available Data Fields

#### Equity Fields (Confirmed Working)
- `PX_LAST` - Last Price
- `CHG_PCT_1D` - 1-Day % Change
- `VOLUME` - Volume
- `PX_BID` - Bid Price
- `PX_ASK` - Ask Price
- `PX_HIGH` - Day High
- `PX_LOW` - Day Low
- `PX_OPEN` - Open Price
- `CUR_MKT_CAP` - Market Cap
- `PE_RATIO` - P/E Ratio

#### FX Fields (Confirmed Working)
- `PX_LAST` - Spot Rate
- `VOLATILITY_30D` - 30-Day Volatility
- `VOLATILITY_90D` - 90-Day Volatility
- `PX_BID` - Bid Rate
- `PX_ASK` - Ask Rate
- `CHG_PCT_1D` - Daily Change %

### 🚨 Known Issues
1. News API requires separate Bloomberg license (~$500-1000/month extra)
2. Some implied volatility fields (IMPLIED_VOL_1M, 1M_ATM_IMP_VOL) not available
3. Azure run-command can get stuck if VM is in "Updating" state

### 🔄 Restart Procedures

#### If API Server Stops:
```powershell
# On the VM
Get-Process python* | Stop-Process -Force -ErrorAction SilentlyContinue
cd C:\Bloomberg\APIServer
C:\Python311\python.exe real_bloomberg_api.py
```

#### From Azure CLI:
```bash
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Process python* | Stop-Process -Force -ErrorAction SilentlyContinue; cd C:\Bloomberg\APIServer; Start-Process C:\Python311\python.exe -ArgumentList 'real_bloomberg_api.py' -WindowStyle Hidden"
```

### 🔐 Access Control
- **NSG Rule**: AllowRDP allows 31.217.174.203
- **API Port**: 8080 open to all sources
- **Windows Firewall**: Bloomberg8080 rule enabled

### 📁 File Locations
- **API Server**: C:\Bloomberg\APIServer\real_bloomberg_api.py
- **Alternative Servers**: 
  - bloomberg_api_server.py (original)
  - bloomberg_full_api.py
  - simple_server.py

### 📝 Last Maintenance Actions
- 2025-07-11 22:39 - Restarted API server with real_bloomberg_api.py
- 2025-07-11 22:40 - Confirmed market data and FX volatility working
- 2025-07-11 - Updated network rules for new IP 31.217.174.203

### ⚠️ Critical Notes
- Bloomberg Terminal must be running and logged in
- API server does NOT auto-start on VM reboot
- Use `real_bloomberg_api.py` for most reliable operation
- Network location changes require NSG rule updates