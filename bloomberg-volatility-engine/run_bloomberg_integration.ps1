# Bloomberg Integration Launcher Script
# Run this after Bloomberg Terminal is installed and running

Write-Host "Bloomberg Azure Integration Launcher" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Check if Bloomberg Terminal is running
$bloombergProcess = Get-Process -Name "wintrv" -ErrorAction SilentlyContinue
if (-not $bloombergProcess) {
    Write-Host "WARNING: Bloomberg Terminal (wintrv.exe) is not running!" -ForegroundColor Red
    Write-Host "Please start Bloomberg Terminal first." -ForegroundColor Yellow
    exit
}

Write-Host "Bloomberg Terminal is running." -ForegroundColor Green

# Set Python alias if needed
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Set-Alias python "C:\Program Files\Python311\python.exe"
}

# Create integration directory
$integrationPath = "C:\BloombergIntegration"
if (!(Test-Path $integrationPath)) {
    New-Item -ItemType Directory -Path $integrationPath -Force
}

Set-Location $integrationPath

# Test Bloomberg API connection
Write-Host "`nTesting Bloomberg API connection..." -ForegroundColor Yellow
python -c "import blpapi; s=blpapi.Session(); s.start(); print('Bloomberg API connection: SUCCESS' if s.start() else 'Bloomberg API connection: FAILED')"

# Create .env file for configuration
$envContent = @"
# Bloomberg Terminal VM Configuration
BLOOMBERG_VM_HOST=172.171.211.16
BLOOMBERG_VM_PRIVATE_IP=10.225.1.4

# Bloomberg API Configuration
BLOOMBERG_API_HOST=localhost
BLOOMBERG_API_PORT=8194

# Azure Configuration (Private Endpoints)
COSMOS_ENDPOINT=https://cosmos-research-analytics-prod.documents.azure.com:443/
COSMOS_DATABASE=bloomberg-data
COSMOS_CONTAINER=market-data

EVENTHUB_NAMESPACE=central-data-hub-eus.servicebus.windows.net
EVENTHUB_NAME=bloomberg-stream

# Key Vault
KEYVAULT_URL=https://bloomberg-kv-1752226585.vault.azure.net/
"@

$envContent | Out-File -FilePath "$integrationPath\.env" -Encoding UTF8

Write-Host "`nConfiguration saved to: $integrationPath\.env" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Ensure Bloomberg Terminal is logged in" -ForegroundColor Cyan
Write-Host "2. Run the integration script: python bloomberg_azure_integration.py" -ForegroundColor Cyan
Write-Host "3. Monitor the output for data streaming to Azure" -ForegroundColor Cyan