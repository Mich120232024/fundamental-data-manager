#!/usr/bin/env python3
"""
Simple direct deployment without external dependencies
"""

import subprocess
import time

def deploy_bloomberg_api():
    """Deploy API server directly via run-command"""
    
    print("🚀 Bloomberg API Server Deployment")
    print("=" * 40)
    
    # PowerShell script to deploy the server
    deployment_script = r'''
# Bloomberg API Server Direct Deployment
Write-Host "Starting deployment..." -ForegroundColor Green

# 1. Setup directory
$path = "C:\Bloomberg\APIServer"
New-Item -ItemType Directory -Force -Path $path | Out-Null
Set-Location $path

# 2. Create the Python API server file
$apiServer = @'
from datetime import datetime

print("Setting up server...")

try:
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="Bloomberg API Server")
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "message": "Bloomberg API Server is running"
        }
    
    @app.get("/")
    async def root():
        return {"message": "Bloomberg API Server", "time": datetime.now().isoformat()}
    
    @app.get("/api/test")  
    async def test():
        return {"test": "successful", "server": "Bloomberg API"}
    
    if __name__ == "__main__":
        print("Starting Bloomberg API Server on port 8080...")
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Installing required packages...")
    import subprocess
    subprocess.run([r"C:\Python311\Scripts\pip.exe", "install", "fastapi", "uvicorn"])
    print("Please run this script again.")
'@

$apiServer | Out-File -FilePath "api_server.py" -Encoding UTF8
Write-Host "API server file created"

# 3. Install packages
Write-Host "Installing packages..."
& C:\Python311\Scripts\pip.exe install fastapi uvicorn --quiet

# 4. Open firewall
New-NetFirewallRule -DisplayName "Bloomberg8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Force -EA SilentlyContinue | Out-Null

# 5. Kill existing processes
Get-Process python* -EA SilentlyContinue | Where-Object {$_.Path -like "*api_server.py*"} | Stop-Process -Force -EA SilentlyContinue

# 6. Start the server
Write-Host "Starting server..."
$proc = Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList "api_server.py" -WorkingDirectory $path -PassThru -WindowStyle Hidden
Write-Host "Server started with PID: $($proc.Id)"

Write-Host "Deployment complete!" -ForegroundColor Green
'''

    # Execute the deployment
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", deployment_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Executing deployment script...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.stdout:
            print("Output:", result.stdout)
        if result.stderr:
            print("Error:", result.stderr)
    except subprocess.TimeoutExpired:
        print("⚠️  Command timed out, but deployment may have succeeded")
    
    print("\n⏳ Waiting 15 seconds for server to start...")
    time.sleep(15)
    
    # Test the server
    print("\n🧪 Testing server connection...")
    test_cmd = ["curl", "-s", "-m", "5", "http://20.172.249.92:8080/health"]
    test_result = subprocess.run(test_cmd, capture_output=True, text=True)
    
    if test_result.returncode == 0 and test_result.stdout:
        print("✅ Server is running!")
        print("Response:", test_result.stdout)
    else:
        print("⚠️  Server not responding yet. It may need more time to start.")
        print("Try testing manually in a minute: curl http://20.172.249.92:8080/health")
    
    print("\n📋 Summary:")
    print("- API Server URL: http://20.172.249.92:8080")
    print("- Health Check: http://20.172.249.92:8080/health")
    print("- API Docs: http://20.172.249.92:8080/docs")


if __name__ == "__main__":
    deploy_bloomberg_api()