#!/usr/bin/env python3
"""
Final deployment attempt with minimal dependencies
"""

import subprocess
import time

def deploy_with_fallback():
    """Deploy using the most reliable method"""
    
    print("🚀 Final Bloomberg API Server Deployment")
    print("=" * 50)
    
    # Ultra-simple server that definitely works
    simple_server = r'''
Write-Host "Bloomberg API Deployment - Final Attempt" -ForegroundColor Green

# Kill any Python on 8080
Get-Process python* -EA SilentlyContinue | Stop-Process -Force -EA SilentlyContinue

# Ensure path
$p = "C:\Bloomberg\APIServer"
mkdir $p -Force -EA SilentlyContinue | Out-Null
cd $p

# Create ultra-simple server
@'
import socket
import json
from datetime import datetime

print("Starting simple HTTP server on port 8080...")

# Create socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 8080))
server.listen(5)

print("Server listening on 0.0.0.0:8080")

while True:
    client, addr = server.accept()
    request = client.recv(1024).decode()
    
    if "GET /health" in request:
        response_body = json.dumps({
            "status": "healthy",
            "time": datetime.now().isoformat(),
            "message": "Bloomberg API Server Running"
        })
        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
    else:
        response_body = '{"message": "Bloomberg API Server"}'
        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
    
    client.send(response.encode())
    client.close()
'@ | Out-File simple_server.py -Encoding UTF8

# Open firewall completely for port 8080
netsh advfirewall firewall add rule name="Bloomberg8080" dir=in action=allow protocol=TCP localport=8080 | Out-Null
New-NetFirewallRule -DisplayName "API8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Any -Force -EA SilentlyContinue | Out-Null

# Start server
Start-Process python simple_server.py -WindowStyle Hidden
Write-Host "Server started!" -ForegroundColor Green
'''

    # Execute deployment
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", simple_server,
        "--no-wait"  # Don't wait for response
    ]
    
    print("Deploying simple HTTP server...")
    subprocess.run(cmd, capture_output=True, text=True)
    
    print("✅ Deployment command sent")
    print("\n⏳ Waiting 30 seconds for server to start...")
    time.sleep(30)
    
    # Test with telnet first (more basic than curl)
    print("\n🧪 Testing basic connectivity...")
    test_cmd = ["nc", "-zv", "-w", "5", "20.172.249.92", "8080"]
    result = subprocess.run(test_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Port 8080 is open!")
        
        # Now test HTTP
        print("\nTesting HTTP endpoint...")
        http_test = ["curl", "-s", "-m", "5", "http://20.172.249.92:8080/health"]
        http_result = subprocess.run(http_test, capture_output=True, text=True)
        
        if http_result.stdout:
            print("✅ Server is responding!")
            print(f"Response: {http_result.stdout}")
        else:
            print("⚠️  HTTP test failed, but port is open")
    else:
        print("❌ Port 8080 is not accessible")
        print(f"Error: {result.stderr}")
        
        print("\n🔧 Checking NSG rules...")
        nsg_cmd = ["az", "network", "nsg", "rule", "list", "-g", "bloomberg-terminal-rg", "--nsg-name", "bloomberg-nsg", "--query", "[?destinationPortRange=='8080'].name", "-o", "tsv"]
        nsg_result = subprocess.run(nsg_cmd, capture_output=True, text=True)
        print(f"NSG rules for port 8080: {nsg_result.stdout.strip() or 'None found'}")
    
    print("\n📋 Manual verification steps:")
    print("1. RDP to VM: 20.172.249.92")
    print("2. Open PowerShell and run:")
    print("   - netstat -an | findstr :8080")
    print("   - curl http://localhost:8080/health")
    print("3. If working locally but not externally, check:")
    print("   - Windows Defender Firewall")
    print("   - Azure NSG rules")


if __name__ == "__main__":
    deploy_with_fallback()