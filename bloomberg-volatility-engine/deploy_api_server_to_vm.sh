#!/bin/bash
# Deploy Bloomberg API Server to VM using Azure CLI run-command

echo "Deploying Bloomberg API Server to VM"
echo "===================================="

RESOURCE_GROUP="bloomberg-terminal-rg"
VM_NAME="bloomberg-vm-02"

# Step 1: Create the directory structure
echo -e "\n1. Creating directory structure on VM..."
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunPowerShellScript \
    --scripts "New-Item -ItemType Directory -Force -Path 'C:\Bloomberg\APIServer' | Out-Null; Write-Host 'Directory created: C:\Bloomberg\APIServer'"

# Step 2: Create test_api_server.py
echo -e "\n2. Creating test_api_server.py..."
cat > /tmp/test_api_server_content.txt << 'EOF'
from fastapi import FastAPI
from datetime import datetime
import uvicorn

app = FastAPI(title="Test Bloomberg API Server")

@app.get("/")
async def root():
    return {"message": "Test Bloomberg API Server is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "server": "Test Bloomberg API Server",
        "timestamp": datetime.now().isoformat(),
        "bloomberg_connected": False,
        "note": "This is a test server without Bloomberg connection"
    }

@app.get("/test")
async def test_endpoint():
    return {
        "test": "successful",
        "server_time": datetime.now().isoformat(),
        "ready_for_bloomberg": True
    }

if __name__ == "__main__":
    print("Starting Test Bloomberg API Server on port 8080...")
    print("Access docs at: http://localhost:8080/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

# Encode content for PowerShell
ENCODED_CONTENT=$(cat /tmp/test_api_server_content.txt | base64 -w 0)

# Write test server file
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunPowerShellScript \
    --scripts "\$content = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('$ENCODED_CONTENT')); Set-Content -Path 'C:\Bloomberg\APIServer\test_api_server.py' -Value \$content -Encoding UTF8; Write-Host 'Created test_api_server.py'"

# Step 3: Install Python packages
echo -e "\n3. Installing Python packages..."
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunPowerShellScript \
    --scripts "cd C:\Bloomberg\APIServer; C:\Python311\Scripts\pip.exe install fastapi uvicorn[standard] python-multipart --no-warn-script-location; Write-Host 'Packages installed'"

# Step 4: Create a simple start script
echo -e "\n4. Creating start script..."
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunPowerShellScript \
    --scripts "Set-Content -Path 'C:\Bloomberg\APIServer\start_test_server.bat' -Value 'cd /d C:\Bloomberg\APIServer && C:\Python311\python.exe test_api_server.py' -Encoding ASCII; Write-Host 'Start script created'"

# Step 5: Configure Windows Firewall
echo -e "\n5. Configuring Windows Firewall..."
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunPowerShellScript \
    --scripts "New-NetFirewallRule -DisplayName 'Bloomberg API Server' -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Any -ErrorAction SilentlyContinue; Write-Host 'Firewall rule configured'"

# Step 6: Start the test server
echo -e "\n6. Starting test server..."
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunPowerShellScript \
    --scripts "Start-Process -FilePath 'C:\Python311\python.exe' -ArgumentList 'C:\Bloomberg\APIServer\test_api_server.py' -WorkingDirectory 'C:\Bloomberg\APIServer' -WindowStyle Hidden; Start-Sleep -Seconds 3; Write-Host 'Test server started'"

echo -e "\n✅ Deployment complete!"
echo "Test the server at: http://20.172.249.92:8080/health"
echo "API docs at: http://20.172.249.92:8080/docs"

# Clean up
rm -f /tmp/test_api_server_content.txt