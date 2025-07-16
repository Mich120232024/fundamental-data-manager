# Bloomberg API VM Setup Guide

## Related Documentation
- **[README](./README.md)**: Complete system overview and API documentation
- **[API Endpoints](./API_ENDPOINTS.md)**: API endpoint documentation for testing
- **[Data Retrieval Methodology](./DATA_RETRIEVAL_METHODOLOGY.md)**: Implementation patterns and performance considerations
- **[Volatility Formats](./VOLATILITY_FORMATS.md)**: Bloomberg security formats and validation
- **[Networking](./NETWORKING.md)**: Network configuration and troubleshooting

## Prerequisites

### Azure Requirements
- Active Azure subscription
- Resource group: `bloomberg-terminal-rg`
- VNet integrated with other Azure services (databases, AKS)
- Azure CLI installed and configured

### Bloomberg Requirements
- Bloomberg Terminal license
- Bloomberg Professional Services account
- Bloomberg API (blpapi) Python package
- Windows VM with Bloomberg Terminal installed

## VM Configuration

### 1. Azure VM Setup
```bash
# Create resource group (if not exists)
az group create --name bloomberg-terminal-rg --location eastus

# Create VNet (integrated with main AKS VNet)
az network vnet create \
  --resource-group bloomberg-terminal-rg \
  --name bloomberg-vnet \
  --address-prefix 10.225.0.0/16 \
  --subnet-name bloomberg-subnet \
  --subnet-prefix 10.225.1.0/24

# Create VM
az vm create \
  --resource-group bloomberg-terminal-rg \
  --name bloomberg-vm-02 \
  --image Win2022Datacenter \
  --admin-username bloombergadmin \
  --admin-password 'Ii89rra137+*' \
  --size Standard_D4s_v3 \
  --vnet-name bloomberg-vnet \
  --subnet bloomberg-subnet \
  --public-ip-address-allocation static \
  --nsg-rule RDP
```

### 2. Network Security Group Rules
```bash
# Allow RDP access
az network nsg rule create \
  --resource-group bloomberg-terminal-rg \
  --nsg-name bloomberg-vm-02NSG \
  --name AllowRDP \
  --protocol tcp \
  --priority 1000 \
  --destination-port-range 3389 \
  --access allow

# Allow API access
az network nsg rule create \
  --resource-group bloomberg-terminal-rg \
  --nsg-name bloomberg-vm-02NSG \
  --name AllowAPI \
  --protocol tcp \
  --priority 1001 \
  --destination-port-range 8080 \
  --access allow

# Allow Bloomberg Terminal ports
az network nsg rule create \
  --resource-group bloomberg-terminal-rg \
  --nsg-name bloomberg-vm-02NSG \
  --name AllowBloomberg \
  --protocol tcp \
  --priority 1002 \
  --destination-port-range 8194 \
  --access allow
```

### 3. VM Network Integration
```bash
# Get VM private IP
VM_PRIVATE_IP=$(az vm show -d -g bloomberg-terminal-rg -n bloomberg-vm-02 --query privateIps -o tsv)
echo "VM Private IP: $VM_PRIVATE_IP"

# Get VM public IP
VM_PUBLIC_IP=$(az vm show -d -g bloomberg-terminal-rg -n bloomberg-vm-02 --query publicIps -o tsv)
echo "VM Public IP: $VM_PUBLIC_IP"
```

## Software Installation

### 1. Connect to VM
```bash
# RDP connection
mstsc /v:20.172.249.92

# Or use Azure Bastion
az network bastion rdp \
  --name bloomberg-bastion \
  --resource-group bloomberg-terminal-rg \
  --target-resource-id /subscriptions/.../bloomberg-vm-02
```

### 2. Install Python 3.11
```powershell
# Download Python 3.11 installer
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe" -OutFile "python-installer.exe"

# Install Python
.\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

# Verify installation
python --version
```

### 3. Install Bloomberg Terminal
```powershell
# Download Bloomberg Terminal installer from Bloomberg
# Follow Bloomberg's installation guide
# Ensure Terminal is installed in default location
```

### 4. Install Bloomberg API
```powershell
# Install Bloomberg Python API
pip install blpapi

# Verify installation
python -c "import blpapi; print('Bloomberg API installed successfully')"
```

## API Server Setup

### 1. Create Directory Structure
```powershell
# Create directories
New-Item -ItemType Directory -Force -Path "C:\BloombergAPI"
New-Item -ItemType Directory -Force -Path "C:\BloombergAPI\logs"

# Set permissions
icacls "C:\BloombergAPI" /grant "Everyone:(OI)(CI)F"
```

### 2. Deploy API Server Code
```powershell
# Create main API server file
# Copy bloomberg-api-fixed.py to C:\BloombergAPI\main.py
# Copy logging_system.py to C:\BloombergAPI\logging_system.py
```

### 3. Install Python Dependencies
```powershell
cd C:\BloombergAPI
pip install fastapi uvicorn blpapi python-multipart
```

### 4. Create Windows Service (Optional)
```powershell
# Install nssm (Non-Sucking Service Manager)
# Download from https://nssm.cc/download

# Create service
nssm install BloombergAPI "C:\Python311\python.exe" "C:\BloombergAPI\main.py"
nssm set BloombergAPI AppDirectory "C:\BloombergAPI"
nssm set BloombergAPI DisplayName "Bloomberg API Server"
nssm set BloombergAPI Description "Bloomberg Terminal API Server"
nssm set BloombergAPI Start SERVICE_AUTO_START

# Start service
nssm start BloombergAPI
```

## Bloomberg Terminal Configuration

### 1. Terminal Installation
- Install Bloomberg Terminal using company-provided installer
- Configure Terminal with company credentials
- Ensure Terminal starts automatically on boot

### 2. API Configuration
- Enable Bloomberg API access
- Configure API port (default 8194)
- Set up authentication for API access

### 3. Terminal Login
- Terminal must be logged in for API to work
- Configure auto-login if possible
- Set up monitoring for login status

## Testing Installation

### 1. Basic Connectivity
```bash
# Test VM accessibility
ping 20.172.249.92

# Test API port
telnet 20.172.249.92 8080
```

### 2. API Health Check
```bash
curl http://20.172.249.92:8080/health
```

Expected response:
```json
{
  "success": true,
  "data": {
    "api_status": "healthy",
    "bloomberg_terminal_running": true,
    "bloomberg_service_available": true
  }
}
```

### 3. Test Live Data Retrieval
```bash
# Test FX rates
curl -X POST http://20.172.249.92:8080/api/fx/rates/live \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pairs": ["EURUSD"]}'

# Test live volatility
curl -X POST http://20.172.249.92:8080/api/fx/volatility/live \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pairs": ["EURUSD"], "tenors": ["1M"]}'
```

### 4. Test EOD Data Retrieval
```bash
# Test EOD volatility
curl -X POST http://20.172.249.92:8080/api/fx/volatility/eod \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pairs": ["EURUSD"], "tenors": ["1M"], "trading_date": "20250716"}'
```

### 5. Test Historical Data Retrieval
```bash
# Test historical volatility
curl -X POST http://20.172.249.92:8080/api/fx/volatility/historical \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pair": "EURUSD", "tenor": "1M", "start_date": "20240101", "end_date": "20250716"}'
```

## Monitoring Setup

### 1. Log Configuration
```powershell
# Create log rotation script
# Set up Windows Task Scheduler for log rotation
schtasks /create /tn "Bloomberg API Log Rotation" /tr "C:\BloombergAPI\rotate_logs.bat" /sc daily /st 00:00
```

### 2. Performance Monitoring
```powershell
# Install performance counters
# Monitor CPU, memory, network usage
# Set up alerts for high resource usage
```

### 3. Health Monitoring
```bash
# Create health check script
# Monitor Bloomberg Terminal status
# Alert on API failures
```

## Security Configuration

### 1. Firewall Rules
```powershell
# Allow API server
New-NetFirewallRule -DisplayName "Bloomberg API" -Direction Inbound -Port 8080 -Protocol TCP -Action Allow

# Allow Bloomberg Terminal
New-NetFirewallRule -DisplayName "Bloomberg Terminal" -Direction Inbound -Port 8194 -Protocol TCP -Action Allow
```

### 2. User Access Control
```powershell
# Create service account
New-LocalUser -Name "BloombergService" -Password (ConvertTo-SecureString "SecurePassword123!" -AsPlainText -Force)

# Grant logon as service right
```

### 3. Data Protection
- Encrypt API keys in configuration
- Use Azure Key Vault for secrets
- Implement proper authentication

## Backup and Recovery

### 1. Configuration Backup
```powershell
# Backup API configuration
Copy-Item -Path "C:\BloombergAPI" -Destination "C:\Backup\BloombergAPI_$(Get-Date -Format 'yyyyMMdd')" -Recurse

# Backup Terminal configuration
# Export Terminal settings
```

### 2. Recovery Procedures
```powershell
# Recovery script for API server
# Restore from backup
# Restart services
```

## Troubleshooting

### Common Issues

#### 1. Bloomberg Terminal Not Starting
```powershell
# Check Terminal installation
Get-Process -Name "bloomberg"

# Check Terminal logs
Get-EventLog -LogName Application -Source "Bloomberg"

# Restart Terminal service
Restart-Service -Name "Bloomberg Terminal"
```

#### 2. API Server Not Responding
```powershell
# Check API server process
Get-Process -Name "python"

# Check API server logs
Get-Content "C:\BloombergAPI\logs\api_requests.log" -Tail 50

# Restart API server
Stop-Process -Name "python" -Force
Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList "C:\BloombergAPI\main.py"
```

#### 3. Network Connectivity Issues
```powershell
# Test internal connectivity
Test-NetConnection -ComputerName localhost -Port 8080

# Test external connectivity
Test-NetConnection -ComputerName 20.172.249.92 -Port 8080

# Check firewall rules
Get-NetFirewallRule -DisplayName "*Bloomberg*"
```

#### 4. Historical Data Issues
```powershell
# Check Bloomberg Terminal license
# Verify historical data permissions
# Check date format in requests (YYYYMMDD)

# Test historical data access
curl -X POST http://20.172.249.92:8080/api/fx/volatility/historical \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pair": "EURUSD", "tenor": "1M", "start_date": "20250715", "end_date": "20250716"}'
```

#### 5. Performance Issues
```powershell
# Monitor CPU usage
Get-Counter "\Processor(_Total)\% Processor Time"

# Monitor memory usage
Get-Counter "\Memory\Available MBytes"

# Check API response times
Get-Content "C:\BloombergAPI\logs\performance.log" | Select-String "slow"
```

### Log Analysis
```powershell
# API request logs
Get-Content "C:\BloombergAPI\logs\api_requests.log" | Select-String "ERROR"

# Bloomberg connection logs
Get-Content "C:\BloombergAPI\logs\bloomberg_connection.log" | Select-String "Failed"

# Performance logs
Get-Content "C:\BloombergAPI\logs\performance.log" | Select-String "slow"
```

## Maintenance

### 1. Regular Updates
- Update Python packages monthly
- Update Bloomberg Terminal quarterly
- Update Windows security patches

### 2. Performance Tuning
- **Monitor API response times** for all data types
- **Optimize batch requests** to reduce API calls
- **Tune Bloomberg connection settings** for optimal performance
- **Implement caching strategies**:
  - Live data: No caching
  - EOD data: Cache until next market close
  - Historical data: Cache with daily refresh
- **Rate limiting**: Implement 10 requests/second limit
- **Connection pooling**: Reuse Bloomberg connections

### 3. Capacity Planning
- **Monitor resource usage** for different data types
- **Plan for increased API usage** during market hours
- **Consider scaling options** for high-frequency requests
- **Implement load balancing** for multiple Bloomberg terminals
- **Data storage planning** for historical data retention

## Environment Variables

```powershell
# Set environment variables
[System.Environment]::SetEnvironmentVariable("BLOOMBERG_API_PORT", "8080", "Machine")
[System.Environment]::SetEnvironmentVariable("BLOOMBERG_TERMINAL_PORT", "8194", "Machine")
[System.Environment]::SetEnvironmentVariable("API_LOG_LEVEL", "INFO", "Machine")
[System.Environment]::SetEnvironmentVariable("BLOOMBERG_CACHE_ENABLED", "true", "Machine")
[System.Environment]::SetEnvironmentVariable("BLOOMBERG_RATE_LIMIT", "10", "Machine")
[System.Environment]::SetEnvironmentVariable("BLOOMBERG_TIMEOUT_LIVE", "5000", "Machine")
[System.Environment]::SetEnvironmentVariable("BLOOMBERG_TIMEOUT_EOD", "8000", "Machine")
[System.Environment]::SetEnvironmentVariable("BLOOMBERG_TIMEOUT_HISTORICAL", "15000", "Machine")
```

## Documentation

### 1. API Documentation
- Maintain endpoint documentation
- Update security procedures
- Document troubleshooting steps

### 2. Operational Procedures
- Document startup/shutdown procedures
- Maintain recovery procedures
- Update monitoring procedures

---

*Last Updated: July 16, 2025*
*Status: Production Ready - Complete Setup Documentation*
*Coverage: Live, EOD, and Historical Data Testing*