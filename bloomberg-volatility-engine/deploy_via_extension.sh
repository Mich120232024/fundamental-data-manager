#!/bin/bash
# Deploy Bloomberg API Server using VM Custom Script Extension

echo "Deploying Bloomberg API Server via VM Extension"
echo "=============================================="

RESOURCE_GROUP="bloomberg-terminal-rg"
VM_NAME="bloomberg-vm-02"
STORAGE_ACCOUNT="bloombergstorage$(date +%s)"
CONTAINER_NAME="deployment"

# Create a simple deployment script
cat > /tmp/deploy_bloomberg_api.ps1 << 'EOF'
# Bloomberg API Server Deployment Script
Write-Host "Starting Bloomberg API Server Deployment" -ForegroundColor Green

# Create directory
$apiPath = "C:\Bloomberg\APIServer"
New-Item -ItemType Directory -Force -Path $apiPath | Out-Null

# Create simple API server
$apiCode = @'
from fastapi import FastAPI
from datetime import datetime
import uvicorn
import os

app = FastAPI(title="Bloomberg API Server")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "Bloomberg API Server",
        "port": 8080,
        "pid": os.getpid()
    }

@app.get("/")
async def root():
    return {"message": "Bloomberg API Server Running", "time": datetime.now().isoformat()}

if __name__ == "__main__":
    print("Starting Bloomberg API Server on port 8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
'@

$apiCode | Out-File -FilePath "$apiPath\api_server.py" -Encoding UTF8

# Install packages
Write-Host "Installing packages..."
& C:\Python311\Scripts\pip.exe install fastapi uvicorn --quiet

# Configure firewall
New-NetFirewallRule -DisplayName "Bloomberg API 8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Any -Force -EA SilentlyContinue

# Kill existing processes
Get-Process python* | Where-Object {$_.CommandLine -like "*api_server.py*"} | Stop-Process -Force -EA SilentlyContinue

# Start the server
Write-Host "Starting server..."
$env:PYTHONUNBUFFERED = "1"
Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList "$apiPath\api_server.py" -WorkingDirectory $apiPath -WindowStyle Hidden

Write-Host "Deployment complete! Server starting on port 8080" -ForegroundColor Green
EOF

# Create storage account for script
echo "Creating temporary storage..."
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location eastus \
    --sku Standard_LRS \
    --only-show-errors

# Get storage key
STORAGE_KEY=$(az storage account keys list \
    --account-name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query "[0].value" -o tsv)

# Create container
az storage container create \
    --name $CONTAINER_NAME \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY \
    --only-show-errors

# Upload script
az storage blob upload \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY \
    --container-name $CONTAINER_NAME \
    --name "deploy_bloomberg_api.ps1" \
    --file "/tmp/deploy_bloomberg_api.ps1" \
    --only-show-errors

# Get blob URL with SAS token
EXPIRY=$(date -u -d "1 hour" '+%Y-%m-%dT%H:%MZ')
SAS_TOKEN=$(az storage blob generate-sas \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY \
    --container-name $CONTAINER_NAME \
    --name "deploy_bloomberg_api.ps1" \
    --permissions r \
    --expiry $EXPIRY \
    --only-show-errors \
    -o tsv)

SCRIPT_URL="https://${STORAGE_ACCOUNT}.blob.core.windows.net/${CONTAINER_NAME}/deploy_bloomberg_api.ps1?${SAS_TOKEN}"

# Run custom script extension
echo "Running deployment script on VM..."
az vm extension set \
    --resource-group $RESOURCE_GROUP \
    --vm-name $VM_NAME \
    --name CustomScriptExtension \
    --publisher Microsoft.Compute \
    --settings "{\"fileUris\": [\"${SCRIPT_URL}\"], \"commandToExecute\": \"powershell -ExecutionPolicy Bypass -File deploy_bloomberg_api.ps1\"}" \
    --only-show-errors

echo "Deployment initiated! Waiting for completion..."
sleep 30

# Clean up storage account
echo "Cleaning up temporary storage..."
az storage account delete \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --yes \
    --only-show-errors

echo -e "\n✅ Deployment complete!"
echo "Test the API server at: http://20.172.249.92:8080/health"