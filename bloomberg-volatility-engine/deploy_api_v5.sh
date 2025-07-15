#!/bin/bash
# Deploy Bloomberg API v5 to Azure VM

echo "🚀 Deploying Bloomberg API v5.0 to Azure VM"
echo "==========================================="

# Step 1: Copy the new API file to clipboard
echo "Step 1: Copy bloomberg_api_v5.py content to clipboard..."
cat bloomberg_api_v5.py | pbcopy
echo "✅ API code copied to clipboard"

# Step 2: Generate PowerShell commands for Azure VM
echo -e "\nStep 2: Azure VM deployment commands:"
echo "--------------------------------------"

cat << 'EOF'
# Run these commands via Azure CLI:

# 1. First, stop the existing API server:
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Process python* | Stop-Process -Force -ErrorAction SilentlyContinue; Write-Host 'API server stopped'"

# 2. Create the new API file (paste the code from clipboard):
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts @'
$apiCode = @"
[PASTE THE BLOOMBERG_API_V5.PY CONTENT HERE]
"@
$apiCode | Out-File -FilePath "C:\Bloomberg\APIServer\bloomberg_api_v5.py" -Encoding UTF8
Write-Host "API v5 file created"
'@

# 3. Start the new API server:
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "cd C:\Bloomberg\APIServer; Start-Process C:\Python311\python.exe -ArgumentList 'bloomberg_api_v5.py' -WindowStyle Hidden; Write-Host 'API v5 started'"

# 4. Verify it's running:
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 \
  --command-id RunPowerShellScript \
  --scripts "Get-Process python* | Select-Object Name, Id, StartTime, Path"
EOF

echo -e "\n✅ Deployment instructions ready"
echo "📋 The API code is in your clipboard - paste it when running command #2"