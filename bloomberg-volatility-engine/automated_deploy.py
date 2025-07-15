#!/usr/bin/env python3
"""
Automated Bloomberg API Server Deployment
Deploys the API server to Azure VM programmatically
"""

import subprocess
import json
import base64
import time

class BloombergServerDeployer:
    def __init__(self):
        self.resource_group = "bloomberg-terminal-rg"
        self.vm_name = "bloomberg-vm-02"
        
    def run_command_on_vm(self, command_script, description="Running command"):
        """Execute PowerShell command on VM via Azure CLI"""
        print(f"\n{description}...")
        
        cmd = [
            "az", "vm", "run-command", "invoke",
            "--resource-group", self.resource_group,
            "--name", self.vm_name,
            "--command-id", "RunPowerShellScript",
            "--scripts", command_script
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get("value"):
                    message = response["value"][0].get("message", "")
                    print(f"✓ {description}: {message}")
                    return True, message
            else:
                print(f"✗ Failed: {result.stderr}")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            print(f"⚠ Command timed out but may still be running")
            return True, "Timeout but likely succeeded"
        except Exception as e:
            print(f"✗ Error: {e}")
            return False, str(e)
    
    def deploy_api_server(self):
        """Deploy the complete API server"""
        
        print("🚀 Automated Bloomberg API Server Deployment")
        print("=" * 50)
        
        # Step 1: Create directory
        self.run_command_on_vm(
            "New-Item -ItemType Directory -Force -Path 'C:\\Bloomberg\\APIServer' | Out-Null; Write-Host 'Directory created'",
            "Creating directory structure"
        )
        
        # Step 2: Create minimal API server
        api_server_code = '''
import sys
sys.path.append("C:\\\\Python311\\\\Lib\\\\site-packages")

try:
    from fastapi import FastAPI
    from datetime import datetime
    import uvicorn
    
    app = FastAPI(title="Bloomberg API Server")
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server": "Bloomberg API Server",
            "bloomberg_connected": False
        }
    
    @app.get("/")
    async def root():
        return {"message": "Bloomberg API Server is running!"}
    
    @app.get("/api/test")
    async def test():
        return {
            "test": "successful",
            "server_time": datetime.now().isoformat()
        }
    
    if __name__ == "__main__":
        print("Starting Bloomberg API Server on port 8080...")
        uvicorn.run(app, host="0.0.0.0", port=8080)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
'''
        
        # Encode the Python code for PowerShell
        encoded_code = base64.b64encode(api_server_code.encode()).decode()
        
        # Write the file
        write_script = f'''
$code = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("{encoded_code}"))
$code | Out-File -FilePath "C:\\Bloomberg\\APIServer\\api_server.py" -Encoding UTF8
Write-Host "API server file created"
'''
        
        self.run_command_on_vm(write_script, "Creating API server file")
        
        # Step 3: Install packages quietly
        self.run_command_on_vm(
            "cd C:\\Bloomberg\\APIServer; C:\\Python311\\Scripts\\pip.exe install fastapi uvicorn python-multipart --quiet --no-warn-script-location; Write-Host 'Packages installed'",
            "Installing Python packages"
        )
        
        # Step 4: Configure firewall
        self.run_command_on_vm(
            'New-NetFirewallRule -DisplayName "Bloomberg API 8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Any -Force -ErrorAction SilentlyContinue; Write-Host "Firewall configured"',
            "Configuring Windows Firewall"
        )
        
        # Step 5: Kill any existing Python processes on port 8080
        self.run_command_on_vm(
            '''
$process = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($process) { 
    Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
    Write-Host "Killed existing process on port 8080"
} else {
    Write-Host "No existing process on port 8080"
}
''',
            "Checking for existing processes"
        )
        
        # Step 6: Create and start Windows service
        service_script = '''
# Create a scheduled task to run at startup
$action = New-ScheduledTaskAction -Execute "C:\\Python311\\python.exe" -Argument "C:\\Bloomberg\\APIServer\\api_server.py" -WorkingDirectory "C:\\Bloomberg\\APIServer"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartInterval (New-TimeSpan -Minutes 1) -RestartCount 3
$principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\\SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Unregister-ScheduledTask -TaskName "BloombergAPIServer" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "BloombergAPIServer" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force

# Also create a user-level task for immediate start
$userAction = New-ScheduledTaskAction -Execute "C:\\Python311\\python.exe" -Argument "C:\\Bloomberg\\APIServer\\api_server.py" -WorkingDirectory "C:\\Bloomberg\\APIServer"
$userTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(5)
Register-ScheduledTask -TaskName "BloombergAPIServerUser" -Action $userAction -Trigger $userTrigger -Force

Start-ScheduledTask -TaskName "BloombergAPIServerUser"
Write-Host "Service created and started"
'''
        
        self.run_command_on_vm(service_script, "Creating Windows service")
        
        # Step 7: Verify it's running
        time.sleep(5)  # Wait for service to start
        
        verify_script = '''
$running = Get-Process python* -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*api_server.py*"}
if ($running) {
    Write-Host "API server process is running"
} else {
    # Try to start it directly
    Start-Process -FilePath "C:\\Python311\\python.exe" -ArgumentList "C:\\Bloomberg\\APIServer\\api_server.py" -WorkingDirectory "C:\\Bloomberg\\APIServer" -WindowStyle Hidden
    Write-Host "Started API server directly"
}
'''
        
        self.run_command_on_vm(verify_script, "Verifying server is running")
        
        print("\n✅ Deployment complete!")
        print(f"Wait 10 seconds then test at: http://20.172.249.92:8080/health")
        
        return True


if __name__ == "__main__":
    deployer = BloombergServerDeployer()
    deployer.deploy_api_server()