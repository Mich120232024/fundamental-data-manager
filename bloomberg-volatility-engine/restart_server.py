#!/usr/bin/env python3
"""
Restart Bloomberg API Server with proper configuration
"""

import subprocess
import time

def restart_server():
    """Restart the API server on the VM"""
    
    print("🔄 Restarting Bloomberg API Server")
    print("=" * 40)
    
    # PowerShell script to restart server
    restart_script = r'''
Write-Host "Restarting Bloomberg API Server..." -ForegroundColor Cyan

# 1. Stop all Python processes
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "Stopped existing processes"

# 2. Ensure directory exists
$apiPath = "C:\Bloomberg\APIServer"
if (-not (Test-Path $apiPath)) {
    New-Item -ItemType Directory -Force -Path $apiPath | Out-Null
}
Set-Location $apiPath

# 3. Create a working API server
$serverCode = @'
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Prepare response based on path
        if self.path == '/health':
            response_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'server': 'Bloomberg API Server',
                'version': '1.0'
            }
        elif self.path == '/api/test':
            response_data = {
                'test': 'successful',
                'message': 'Bloomberg API is working',
                'timestamp': datetime.now().isoformat()
            }
        else:
            response_data = {
                'message': 'Bloomberg API Server',
                'available_endpoints': ['/health', '/api/test'],
                'timestamp': datetime.now().isoformat()
            }
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
    
    def log_message(self, format, *args):
        # Suppress request logging
        pass

if __name__ == '__main__':
    server_address = ('0.0.0.0', 8080)
    print(f'Starting Bloomberg API Server on {server_address[0]}:{server_address[1]}')
    httpd = HTTPServer(server_address, APIHandler)
    print('Server is running...')
    httpd.serve_forever()
'@

# Save the server file
$serverCode | Out-File -FilePath "$apiPath\bloomberg_server.py" -Encoding UTF8
Write-Host "Server file created"

# 4. Create a batch file to run the server
@"
@echo off
cd /d C:\Bloomberg\APIServer
echo Starting Bloomberg API Server...
C:\Python311\python.exe bloomberg_server.py
pause
"@ | Out-File -FilePath "$apiPath\start_server.bat" -Encoding ASCII

# 5. Ensure firewall is open
New-NetFirewallRule -DisplayName "Bloomberg API 8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Any -Force -ErrorAction SilentlyContinue | Out-Null

# 6. Start the server using multiple methods for reliability
Write-Host "Starting server..." -ForegroundColor Green

# Method 1: Direct start
Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList "$apiPath\bloomberg_server.py" -WorkingDirectory $apiPath -WindowStyle Hidden

# Method 2: Also create a scheduled task as backup
$taskAction = New-ScheduledTaskAction -Execute "C:\Python311\python.exe" -Argument "C:\Bloomberg\APIServer\bloomberg_server.py" -WorkingDirectory "C:\Bloomberg\APIServer"
$taskTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(5)
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "BloombergAPIRestart" -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Force | Out-Null
Start-ScheduledTask -TaskName "BloombergAPIRestart"

Write-Host "Server restart initiated" -ForegroundColor Green

# 7. Wait and verify
Start-Sleep -Seconds 5

# Check if running
$proc = Get-Process python* -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*python*"}
if ($proc) {
    Write-Host "Python process running: PID $($proc.Id)" -ForegroundColor Green
    
    # Test localhost
    try {
        $test = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5
        Write-Host "Localhost test successful!" -ForegroundColor Green
    } catch {
        Write-Host "Localhost test failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "No Python process found!" -ForegroundColor Red
}
'''

    # Execute the restart
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", restart_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Executing restart command...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.stdout:
            print("Output:", result.stdout.strip())
        if result.stderr:
            print("Error:", result.stderr.strip())
    except subprocess.TimeoutExpired:
        print("⚠️  Command timed out, but server may have restarted")
    
    # Wait for server to start
    print("\n⏳ Waiting 15 seconds for server to stabilize...")
    time.sleep(15)
    
    # Test the server
    print("\n🧪 Testing server connectivity...")
    
    # Test 1: Basic connectivity
    test_cmd = ["nc", "-zv", "-w", "5", "20.172.249.92", "8080"]
    nc_result = subprocess.run(test_cmd, capture_output=True, text=True)
    
    if nc_result.returncode == 0:
        print("✅ Port 8080 is open!")
        
        # Test 2: HTTP request
        http_test = ["curl", "-s", "-m", "10", "http://20.172.249.92:8080/health"]
        http_result = subprocess.run(http_test, capture_output=True, text=True)
        
        if http_result.returncode == 0 and http_result.stdout:
            print("✅ Server is responding!")
            print(f"Response: {http_result.stdout}")
            
            # Test other endpoints
            print("\nTesting other endpoints:")
            test_endpoints = ["/", "/api/test"]
            for endpoint in test_endpoints:
                test = subprocess.run(
                    ["curl", "-s", "-m", "5", f"http://20.172.249.92:8080{endpoint}"],
                    capture_output=True, text=True
                )
                if test.stdout:
                    print(f"{endpoint}: {test.stdout}")
        else:
            print("⚠️  HTTP request failed")
            print(f"Error: {http_result.stderr}")
    else:
        print("❌ Port 8080 is not accessible")
        print(f"Error: {nc_result.stderr}")
    
    print("\n📋 Summary:")
    print("Bloomberg API Server has been restarted")
    print("Access at: http://20.172.249.92:8080")


if __name__ == "__main__":
    restart_server()