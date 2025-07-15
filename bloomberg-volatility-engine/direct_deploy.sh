#!/bin/bash
# Direct deployment using existing storage account

echo "Direct Bloomberg API Server Deployment"
echo "====================================="

RESOURCE_GROUP="bloomberg-terminal-rg"
VM_NAME="bloomberg-vm-02"

# Create deployment script
cat > /tmp/deploy_api.ps1 << 'EOF'
Write-Host "Bloomberg API Server Deployment" -ForegroundColor Cyan

# Ensure directory exists
$path = "C:\Bloomberg\APIServer"
New-Item -ItemType Directory -Force -Path $path | Out-Null
cd $path

# Kill any existing Python processes on port 8080
Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    try {
        $tcp = Get-NetTCPConnection -OwningProcess $_.Id -LocalPort 8080 -ErrorAction SilentlyContinue
        $tcp -ne $null
    } catch { $false }
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Create API server
@'
from fastapi import FastAPI
from datetime import datetime
import uvicorn

app = FastAPI(title="Bloomberg API Server", version="1.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.now().isoformat(), "server": "Bloomberg API"}

@app.get("/")
async def root():
    return {"message": "Bloomberg API Server is running!"}

print("Starting server on http://0.0.0.0:8080")
uvicorn.run(app, host="0.0.0.0", port=8080)
'@ | Out-File -FilePath "api_server.py" -Encoding UTF8

# Install packages silently
C:\Python311\Scripts\pip.exe install fastapi uvicorn --quiet --no-warn-script-location

# Configure firewall
New-NetFirewallRule -DisplayName "API8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Force -EA SilentlyContinue | Out-Null

# Start server in background
$pythonPath = "C:\Python311\python.exe"
$scriptPath = "C:\Bloomberg\APIServer\api_server.py"
Start-Process -FilePath $pythonPath -ArgumentList $scriptPath -WorkingDirectory $path -WindowStyle Hidden

Write-Host "API Server deployed and starting..." -ForegroundColor Green
EOF

# Use existing storage account
STORAGE_ACCOUNT="fredcatalog4f6a73c5"
CONTAINER="deployment-scripts"

# Upload script
echo "Uploading deployment script..."
az storage blob upload \
    --account-name $STORAGE_ACCOUNT \
    --container-name $CONTAINER \
    --name "deploy_api.ps1" \
    --file "/tmp/deploy_api.ps1" \
    --auth-mode login \
    --overwrite \
    --only-show-errors

# Get blob URL
BLOB_URL="https://${STORAGE_ACCOUNT}.blob.core.windows.net/${CONTAINER}/deploy_api.ps1"

# Create SAS token (1 hour expiry)
END_TIME=$(python3 -c "from datetime import datetime, timedelta; print((datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'))")

SAS_TOKEN=$(az storage blob generate-sas \
    --account-name $STORAGE_ACCOUNT \
    --container-name $CONTAINER \
    --name "deploy_api.ps1" \
    --permissions r \
    --expiry $END_TIME \
    --auth-mode login \
    --as-user \
    --full-uri \
    --only-show-errors \
    -o tsv)

echo "Running deployment on VM..."

# Method 1: Try with custom script extension
az vm extension set \
    --resource-group $RESOURCE_GROUP \
    --vm-name $VM_NAME \
    --name CustomScriptExtension \
    --publisher Microsoft.Compute \
    --force-update \
    --settings "{\"fileUris\": [\"${SAS_TOKEN}\"], \"commandToExecute\": \"powershell -ExecutionPolicy Bypass -File deploy_api.ps1\"}" \
    --no-wait \
    --only-show-errors

echo "Deployment initiated. Waiting 30 seconds for server to start..."
sleep 30

# Test the deployment
echo -e "\nTesting deployment..."
curl -s -m 5 http://20.172.249.92:8080/health || echo "Server may still be starting..."

echo -e "\n✅ Deployment script executed"
echo "Test URL: http://20.172.249.92:8080/health"
echo "API Docs: http://20.172.249.92:8080/docs"

# Clean up
rm -f /tmp/deploy_api.ps1