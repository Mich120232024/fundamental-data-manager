#!/usr/bin/env python3
"""
Restart Bloomberg API server on VM
"""

import subprocess
import time

def restart_api_server():
    """Restart the Bloomberg API server"""
    
    print("🔄 Restarting Bloomberg API Server")
    print("=" * 60)
    
    restart_script = r'''
Write-Host "Restarting Bloomberg API Server..." -ForegroundColor Yellow

# Kill any existing Python processes running the API
Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*bloomberg_api_server*" -or 
    $_.Path -like "*python*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Stopped existing processes"

# Wait a moment
Start-Sleep -Seconds 3

# Start the API server
$apiScript = @'
import os
os.chdir(r"C:\Bloomberg\APIServer")
exec(open("bloomberg_api_server.py").read())
'@

# Save and run
$apiScript | Out-File -FilePath "C:\Bloomberg\APIServer\start_api.py" -Encoding UTF8

Write-Host "Starting API server..."
Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList "C:\Bloomberg\APIServer\start_api.py" -WorkingDirectory "C:\Bloomberg\APIServer" -WindowStyle Hidden

Start-Sleep -Seconds 5

# Check if it's running
$response = try { 
    Invoke-WebRequest -Uri "http://localhost:8080/api/health" -UseBasicParsing -TimeoutSec 5
    $true
} catch { 
    $false 
}

if ($response) {
    Write-Host "✓ API Server is running!" -ForegroundColor Green
    $health = Invoke-RestMethod -Uri "http://localhost:8080/api/health"
    Write-Host "Bloomberg connected: $($health.bloomberg_connected)"
} else {
    Write-Host "✗ API Server failed to start" -ForegroundColor Red
    Write-Host "Checking logs..."
    
    # Try to start directly
    Write-Host "Attempting direct start..."
    cd C:\Bloomberg\APIServer
    Start-Process cmd -ArgumentList "/c C:\Python311\python.exe bloomberg_api_server.py > api_log.txt 2>&1" -WindowStyle Hidden
    
    Start-Sleep -Seconds 5
    
    # Check again
    $response2 = try { 
        Invoke-WebRequest -Uri "http://localhost:8080/api/health" -UseBasicParsing -TimeoutSec 5
        $true
    } catch { 
        $false 
    }
    
    if ($response2) {
        Write-Host "✓ API Server started on second attempt!" -ForegroundColor Green
    } else {
        Write-Host "Check C:\Bloomberg\APIServer\api_log.txt for errors"
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan
'''

    # Execute restart
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", restart_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Restarting API server on Bloomberg VM...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("Command timed out but server may be starting...")
    
    # Wait and test
    print("\nWaiting for server to start...")
    time.sleep(10)
    
    print("\nTesting connection...")
    test_cmd = ["curl", "-s", "http://20.172.249.92:8080/api/health"]
    test_result = subprocess.run(test_cmd, capture_output=True, text=True)
    
    if test_result.stdout:
        print("API Response:", test_result.stdout)
    else:
        print("No response from API server")


if __name__ == "__main__":
    restart_api_server()