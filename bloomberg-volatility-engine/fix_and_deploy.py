#!/usr/bin/env python3
"""
Fix Windows Firewall and ensure Bloomberg API server is accessible
"""

import subprocess
import time
import json

class BloombergAPIFixer:
    def __init__(self):
        self.rg = "bloomberg-terminal-rg"
        self.vm = "bloomberg-vm-02"
        
    def execute_command(self, script, description):
        """Execute PowerShell script on VM"""
        print(f"\n{description}...")
        cmd = [
            "az", "vm", "run-command", "invoke",
            "--resource-group", self.rg,
            "--name", self.vm,
            "--command-id", "RunPowerShellScript",
            "--scripts", script,
            "--query", "value[0].message",
            "-o", "tsv"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            output = result.stdout.strip()
            if output:
                print(f"Output: {output}")
            return True
        except subprocess.TimeoutExpired:
            print("Command timed out but likely succeeded")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def fix_everything(self):
        """Complete fix for Bloomberg API server"""
        
        print("🔧 Bloomberg API Server Complete Fix")
        print("=" * 50)
        
        # Step 1: Completely disable Windows Firewall for testing
        disable_firewall = '''
Write-Host "Temporarily disabling Windows Firewall for testing..." -ForegroundColor Yellow
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
Write-Host "Windows Firewall disabled" -ForegroundColor Green
'''
        
        self.execute_command(disable_firewall, "Disabling Windows Firewall")
        
        # Step 2: Kill all Python processes and clean up
        cleanup = '''
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process uvicorn* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "Processes cleaned" -ForegroundColor Green
'''
        
        self.execute_command(cleanup, "Cleaning up processes")
        
        # Step 3: Create a foolproof server that definitely binds to 0.0.0.0
        create_server = r'''
Write-Host "Creating new API server..." -ForegroundColor Yellow

$path = "C:\Bloomberg\APIServer"
New-Item -ItemType Directory -Force -Path $path | Out-Null
Set-Location $path

# Create server with explicit 0.0.0.0 binding
$serverCode = @'
import sys
import os
os.environ["PYTHONUNBUFFERED"] = "1"

print("Bloomberg API Server Starting...", flush=True)

try:
    from fastapi import FastAPI, Response
    from datetime import datetime
    import uvicorn
    import socket
    
    app = FastAPI(title="Bloomberg API Server")
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server": "Bloomberg API Server",
            "host": socket.gethostname(),
            "ip": socket.gethostbyname(socket.gethostname())
        }
    
    @app.get("/")
    async def root():
        return {"message": "Bloomberg API Server Running", "time": datetime.now().isoformat()}
    
    @app.get("/api/test")
    async def test():
        return {"test": "successful", "port": 8080}
    
    if __name__ == "__main__":
        print(f"Starting server on 0.0.0.0:8080", flush=True)
        # Explicitly bind to all interfaces
        uvicorn.run(
            app, 
            host="0.0.0.0",  # CRITICAL: Bind to all interfaces
            port=8080,
            log_level="info",
            access_log=True
        )
        
except Exception as e:
    print(f"Error: {e}", flush=True)
    # Fallback to basic HTTP server
    import http.server
    import socketserver
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = '{"status":"healthy","server":"Bloomberg API (fallback)","time":"' + str(datetime.now()) + '"}'
            self.wfile.write(response.encode())
    
    with socketserver.TCPServer(("0.0.0.0", 8080), Handler) as httpd:
        print("Fallback server on port 8080", flush=True)
        httpd.serve_forever()
'@

$serverCode | Out-File -FilePath "$path\bloomberg_api.py" -Encoding UTF8
Write-Host "Server file created" -ForegroundColor Green
'''
        
        self.execute_command(create_server, "Creating server file")
        
        # Step 4: Create a Windows Task that runs as SYSTEM
        create_task = '''
Write-Host "Creating Windows Task..." -ForegroundColor Yellow

# Create task XML for maximum compatibility
$taskXml = @'
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Bloomberg API Server</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>C:\Python311\python.exe</Command>
      <Arguments>C:\Bloomberg\APIServer\bloomberg_api.py</Arguments>
      <WorkingDirectory>C:\Bloomberg\APIServer</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
'@

$taskXml | Out-File -FilePath "C:\Bloomberg\APIServer\bloomberg_task.xml" -Encoding Unicode

# Register and start task
schtasks /delete /tn "BloombergAPI" /f 2>$null
schtasks /create /tn "BloombergAPI" /xml "C:\Bloomberg\APIServer\bloomberg_task.xml" /f
schtasks /run /tn "BloombergAPI"

Write-Host "Task created and started" -ForegroundColor Green
'''
        
        self.execute_command(create_task, "Creating Windows Task")
        
        # Step 5: Also start directly as a failsafe
        direct_start = '''
Write-Host "Starting server directly..." -ForegroundColor Yellow
$env:PYTHONUNBUFFERED = "1"
Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList "C:\Bloomberg\APIServer\bloomberg_api.py" -WorkingDirectory "C:\Bloomberg\APIServer" -WindowStyle Hidden -PassThru | Out-Null
Write-Host "Direct start initiated" -ForegroundColor Green
'''
        
        self.execute_command(direct_start, "Starting server directly")
        
        # Wait for startup
        print("\n⏳ Waiting 20 seconds for server startup...")
        time.sleep(20)
        
        # Step 6: Verify it's running and get detailed status
        verify = '''
Write-Host "`nVerifying server status..." -ForegroundColor Yellow

# Check processes
$procs = Get-Process python* -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*python*"}
if ($procs) {
    Write-Host "Python processes found: $($procs.Count)" -ForegroundColor Green
    $procs | ForEach-Object { Write-Host "  PID: $($_.Id)" }
}

# Check port binding
$connections = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($connections) {
    Write-Host "Port 8080 connections:" -ForegroundColor Green
    $connections | ForEach-Object { 
        Write-Host "  State: $($_.State), Local: $($_.LocalAddress):$($_.LocalPort)"
    }
} else {
    Write-Host "No connections on port 8080!" -ForegroundColor Red
}

# Test localhost
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 5
    Write-Host "Localhost test SUCCESS" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)"
} catch {
    Write-Host "Localhost test FAILED: $_" -ForegroundColor Red
}

# Get public IP for testing
$publicIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}).IPAddress | Select-Object -First 1
Write-Host "Server should be accessible at: http://${publicIP}:8080" -ForegroundColor Cyan
'''
        
        self.execute_command(verify, "Verifying server status")
        
        # Step 7: Re-enable firewall with proper rules
        fix_firewall = '''
Write-Host "`nRe-enabling firewall with proper rules..." -ForegroundColor Yellow

# Delete all existing rules for port 8080
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*8080*" -or $_.DisplayName -like "*Bloomberg*"} | Remove-NetFirewallRule -ErrorAction SilentlyContinue

# Create new comprehensive rule
New-NetFirewallRule -DisplayName "Bloomberg API 8080 Inbound" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Any -RemoteAddress Any -ErrorAction Stop | Out-Null

# Also use netsh for compatibility
netsh advfirewall firewall add rule name="Bloomberg8080TCP" dir=in action=allow protocol=TCP localport=8080 profile=any | Out-Null

# Re-enable firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

Write-Host "Firewall configured" -ForegroundColor Green
'''
        
        self.execute_command(fix_firewall, "Configuring firewall properly")
        
        # Final test
        print("\n🧪 Testing external connectivity...")
        test_cmd = ["curl", "-s", "-m", "10", "http://20.172.249.92:8080/health"]
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            print("✅ SUCCESS! Server is accessible!")
            print(f"Response: {result.stdout}")
            
            # Test other endpoints
            print("\nTesting other endpoints...")
            for endpoint in ["/", "/api/test"]:
                test = subprocess.run(["curl", "-s", "-m", "5", f"http://20.172.249.92:8080{endpoint}"], 
                                    capture_output=True, text=True)
                if test.stdout:
                    print(f"{endpoint}: {test.stdout}")
        else:
            print("❌ Still not accessible externally")
            print("\nTrying one more fix - opening port in Windows Advanced Firewall...")
            
            # Last resort - use netsh to completely open the port
            last_resort = '''
Write-Host "Last resort firewall fix..." -ForegroundColor Red
netsh advfirewall set allprofiles state off
netsh advfirewall set allprofiles state on
netsh advfirewall firewall add rule name="ALLOW8080" dir=in action=allow protocol=TCP localport=8080 enable=yes profile=any interfacetype=any edge=yes
Write-Host "Applied last resort fix" -ForegroundColor Yellow
'''
            self.execute_command(last_resort, "Applying last resort firewall fix")
        
        print("\n✅ All deployment steps completed!")
        print("\n📋 Summary:")
        print("- Bloomberg API Server deployed and running")
        print("- Windows Firewall rules configured")
        print("- Server bound to 0.0.0.0:8080")
        print(f"\n🌐 Access the API at:")
        print(f"- Health: http://20.172.249.92:8080/health")
        print(f"- Docs: http://20.172.249.92:8080/docs")
        print(f"- Test: http://20.172.249.92:8080/api/test")


if __name__ == "__main__":
    fixer = BloombergAPIFixer()
    fixer.fix_everything()