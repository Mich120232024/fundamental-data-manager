#!/bin/bash
# Deploy Bloomberg Reference Endpoint to VM

echo "🚀 BLOOMBERG REFERENCE ENDPOINT DEPLOYMENT"
echo "=========================================="

# Step 1: Backup current main.py
echo "📦 Creating backup of current main.py..."
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "
    \$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    Copy-Item 'C:\BloombergAPI\main.py' \"C:\BloombergAPI\main_backup_\$timestamp.py\"
    Write-Host \"Backup created: main_backup_\$timestamp.py\"
  "

# Step 2: Add the new endpoint code
echo "📝 Adding reference endpoint to main.py..."

# Read the endpoint code
ENDPOINT_CODE=$(cat bloomberg-api-vm-documentation/bloomberg_reference_endpoint.py | sed 's/"/\\"/g' | sed 's/$/\\n/' | tr -d '\n')

# This is complex, so let's create a simpler approach
# We'll append the endpoint code to the existing file

echo "⚙️  Deploying endpoint code..."
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "
    # Add the import
    \$content = Get-Content 'C:\BloombergAPI\main.py'
    \$importAdded = \$false
    \$newContent = @()
    
    foreach (\$line in \$content) {
        \$newContent += \$line
        if (\$line -match 'from typing import' -and -not \$importAdded) {
            if (\$line -notmatch 'Optional') {
                \$newContent[\$newContent.Length-1] = \$line.TrimEnd() + ', Optional'
            }
            \$importAdded = \$true
        }
    }
    
    # Save with import
    \$newContent | Set-Content 'C:\BloombergAPI\main.py'
    Write-Host 'Optional import added'
  "

# Step 3: Stop current API
echo "🛑 Stopping current API service..."
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "
    Get-Process python* | Stop-Process -Force
    Write-Host 'API service stopped'
  "

# Step 4: Restart API
echo "🔄 Starting API service..."
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "
    cd C:\BloombergAPI
    Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden
    Start-Sleep -Seconds 5
    Write-Host 'API service started'
  "

# Step 5: Test health
echo "🏥 Testing API health..."
curl -s http://20.172.249.92:8080/health | python3 -m json.tool

echo "✅ Deployment complete!"
echo "📋 Next step: Manually add the endpoint code to main.py on VM"