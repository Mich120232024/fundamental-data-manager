#!/bin/bash
# Deploy using Azure VM Extension - more reliable than run-command

echo "🚀 Bloomberg API Server Deployment via VM Extension"
echo "=================================================="

RG="bloomberg-terminal-rg"
VM="bloomberg-vm-02"

# Create inline script for VM extension
SCRIPT='powershell -ExecutionPolicy Bypass -Command "
Write-Host \"Bloomberg API Server Setup\" -ForegroundColor Green

# 1. Disable firewall temporarily
Set-NetFirewallProfile -All -Enabled False

# 2. Kill existing Python
Get-Process python* -EA SilentlyContinue | Stop-Process -Force

# 3. Setup directory
\$p = \"C:\\Bloomberg\\APIServer\"
New-Item -ItemType Directory -Force -Path \$p | Out-Null
Set-Location \$p

# 4. Create simple HTTP server
\$code = @\"
import http.server
import json
from datetime import datetime

class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == \"/health\":
            response = {\"status\": \"healthy\", \"time\": str(datetime.now()), \"server\": \"Bloomberg API\"}
        else:
            response = {\"message\": \"Bloomberg API Server\", \"endpoint\": self.path}
        
        self.send_response(200)
        self.send_header(\"Content-Type\", \"application/json\")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        return  # Suppress logs

print(\"Starting Bloomberg API Server on port 8080...\")
server = http.server.HTTPServer((\"0.0.0.0\", 8080), APIHandler)
server.serve_forever()
\"@

\$code | Out-File -FilePath \"simple_api.py\" -Encoding UTF8

# 5. Install as service using NSSM if available, otherwise use Task Scheduler
\$serviceName = \"BloombergAPI\"
schtasks /delete /tn \$serviceName /f 2>\$null

\$action = New-ScheduledTaskAction -Execute \"C:\\Python311\\python.exe\" -Argument \"C:\\Bloomberg\\APIServer\\simple_api.py\"
\$trigger = New-ScheduledTaskTrigger -AtStartup
\$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName \$serviceName -Action \$action -Trigger \$trigger -Settings \$settings -User \"SYSTEM\" -RunLevel Highest -Force

Start-ScheduledTask -TaskName \$serviceName

# 6. Open firewall
Start-Sleep -Seconds 5
New-NetFirewallRule -DisplayName \"API8080\" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Any -Force
Set-NetFirewallProfile -All -Enabled True

Write-Host \"Setup complete!\" -ForegroundColor Green
"'

# Remove any existing extension
echo "Removing existing extensions..."
az vm extension delete \
    --resource-group $RG \
    --vm-name $VM \
    --name CustomScriptExtension \
    --no-wait \
    2>/dev/null

sleep 10

# Deploy new extension
echo "Deploying Bloomberg API Server..."
az vm extension set \
    --resource-group $RG \
    --vm-name $VM \
    --name CustomScriptExtension \
    --publisher Microsoft.Compute \
    --version 1.10 \
    --settings "{\"commandToExecute\": \"$SCRIPT\"}" \
    --no-wait

echo "⏳ Waiting 45 seconds for deployment..."
sleep 45

# Test the server
echo -e "\n🧪 Testing server..."
if curl -s -m 10 http://20.172.249.92:8080/health | jq . 2>/dev/null; then
    echo -e "\n✅ SUCCESS! Bloomberg API Server is running!"
    echo "Endpoints:"
    echo "  - http://20.172.249.92:8080/health"
    echo "  - http://20.172.249.92:8080/"
else
    echo -e "\n⚠️  Server not responding yet. Checking VM extension status..."
    az vm extension show \
        --resource-group $RG \
        --vm-name $VM \
        --name CustomScriptExtension \
        --query "provisioningState" \
        -o tsv
fi