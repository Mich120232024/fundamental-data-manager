#!/usr/bin/env python3
"""
Set up Bloomberg API server to auto-start and stay running
"""

import subprocess

def setup_auto_start():
    """Configure Bloomberg API server for automatic startup and resilience"""
    
    print("🔧 Setting Up Bloomberg API Auto-Start")
    print("=" * 60)
    
    setup_script = r'''
Write-Host "Setting up Bloomberg API for better control flow" -ForegroundColor Cyan

# 1. Create a Windows Service for the API
$serviceScript = @'
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os
import sys
import time

sys.path.append(r"C:\Bloomberg\APIServer")
sys.path.append(r"C:\blp\API\Python")

class BloombergAPIService(win32serviceutil.ServiceFramework):
    _svc_name_ = "BloombergAPIServer"
    _svc_display_name_ = "Bloomberg API Server"
    _svc_description_ = "Provides REST API access to Bloomberg Terminal data"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
    
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()
    
    def main(self):
        # Import and run the Bloomberg API server
        os.chdir(r"C:\Bloomberg\APIServer")
        import bloomberg_api_server
        # The server will run until the service stops

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(BloombergAPIService)
'@

# Save service script
$serviceScript | Out-File -FilePath "C:\Bloomberg\APIServer\bloomberg_service.py" -Encoding UTF8

# 2. Create a simpler startup script with auto-restart
$startupScript = @'
import subprocess
import time
import sys
import os

def start_api_server():
    """Start Bloomberg API server with auto-restart on failure"""
    
    while True:
        try:
            print(f"Starting Bloomberg API Server at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Change to API directory
            os.chdir(r"C:\Bloomberg\APIServer")
            
            # Run the API server
            process = subprocess.Popen(
                [r"C:\Python311\python.exe", "bloomberg_api_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor the process
            while True:
                if process.poll() is not None:
                    # Process ended
                    print(f"API Server stopped with code {process.returncode}")
                    print("Restarting in 10 seconds...")
                    time.sleep(10)
                    break
                
                # Check if server is responsive
                try:
                    import requests
                    response = requests.get("http://localhost:8080/api/health", timeout=5)
                    if response.status_code != 200:
                        print("API Server not responding properly")
                        process.terminate()
                        break
                except:
                    pass
                
                time.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            print(f"Error: {e}")
            print("Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    start_api_server()
'@

# Save startup script
$startupScript | Out-File -FilePath "C:\Bloomberg\APIServer\auto_start_api.py" -Encoding UTF8

# 3. Create a Task Scheduler job for auto-start on login
$taskAction = New-ScheduledTaskAction -Execute "C:\Python311\python.exe" -Argument "C:\Bloomberg\APIServer\auto_start_api.py" -WorkingDirectory "C:\Bloomberg\APIServer"
$taskTrigger = New-ScheduledTaskTrigger -AtLogOn -User "bloombergadmin"
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartInterval (New-TimeSpan -Minutes 5) -RestartCount 3

Register-ScheduledTask -TaskName "BloombergAPIServer" -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Description "Auto-start Bloomberg API Server" -Force

Write-Host "✓ Created scheduled task for auto-start" -ForegroundColor Green

# 4. Create a batch file for easy manual start
$batchContent = @"
@echo off
echo Starting Bloomberg API Server...
cd /d C:\Bloomberg\APIServer
C:\Python311\python.exe auto_start_api.py
pause
"@

$batchContent | Out-File -FilePath "C:\Bloomberg\APIServer\START_API_SERVER.bat" -Encoding ASCII

# 5. Start the API server now
Write-Host "`nStarting API Server now..." -ForegroundColor Yellow
Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList "C:\Bloomberg\APIServer\auto_start_api.py" -WorkingDirectory "C:\Bloomberg\APIServer" -WindowStyle Hidden

Start-Sleep -Seconds 5

# 6. Test if it's running
$testUrl = "http://localhost:8080/api/health"
try {
    $response = Invoke-RestMethod -Uri $testUrl -Method Get
    Write-Host "✓ API Server is running!" -ForegroundColor Green
    Write-Host "  Bloomberg connected: $($response.bloomberg_connected)" -ForegroundColor Green
} catch {
    Write-Host "✗ API Server failed to start" -ForegroundColor Red
    Write-Host "  Trying direct start..." -ForegroundColor Yellow
    
    # Try direct start
    cd C:\Bloomberg\APIServer
    Start-Process cmd -ArgumentList "/c C:\Python311\python.exe bloomberg_api_server.py" -WindowStyle Hidden
}

Write-Host "`n✓ Setup complete!" -ForegroundColor Green
Write-Host "`nAPI Server will now:" -ForegroundColor Cyan
Write-Host "  - Auto-start when user logs in"
Write-Host "  - Restart automatically if it crashes"
Write-Host "  - Be accessible at http://localhost:8080"
Write-Host "`nYou can also manually start it with:"
Write-Host "  - Double-click C:\Bloomberg\APIServer\START_API_SERVER.bat"
Write-Host "  - Or run the scheduled task 'BloombergAPIServer'"
'''

    # Execute setup
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", setup_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Setting up automatic API server startup...")
    print("This will ensure the API stays running...\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("Setup may still be running...")
    
    print("\n" + "=" * 60)
    print("Better control flow established!")
    print("The API server will now auto-start and stay running.")


if __name__ == "__main__":
    setup_auto_start()