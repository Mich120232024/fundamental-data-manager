# Quick Deploy Bloomberg API Server
# Run this directly on the VM as Administrator

Write-Host "Quick Deploy Bloomberg API Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Create directory
$apiPath = "C:\Bloomberg\APIServer"
New-Item -ItemType Directory -Force -Path $apiPath | Out-Null
Set-Location $apiPath

# Create the API server script
$apiServerCode = @'
from fastapi import FastAPI
from datetime import datetime
import uvicorn

app = FastAPI(title="Bloomberg API Server")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bloomberg_connected": False,
        "note": "Test server running"
    }

@app.get("/api/test")
async def test():
    return {"message": "Bloomberg API Server is running!", "time": datetime.now().isoformat()}

if __name__ == "__main__":
    print("Starting Bloomberg API Server on http://0.0.0.0:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
'@

$apiServerCode | Out-File -FilePath "$apiPath\bloomberg_api_server.py" -Encoding UTF8

# Install required packages
Write-Host "`nInstalling packages..." -ForegroundColor Yellow
& C:\Python311\Scripts\pip.exe install fastapi uvicorn --quiet

# Create start script
@"
@echo off
cd /d C:\Bloomberg\APIServer
C:\Python311\python.exe bloomberg_api_server.py
pause
"@ | Out-File -FilePath "$apiPath\start_server.bat" -Encoding ASCII

# Configure firewall
Write-Host "`nConfiguring firewall..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Bloomberg API Port 8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Any -ErrorAction SilentlyContinue

# Start the server
Write-Host "`nStarting server..." -ForegroundColor Yellow
Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList "bloomberg_api_server.py" -WorkingDirectory $apiPath -WindowStyle Minimized

Write-Host "`n✅ Server should be starting on port 8080" -ForegroundColor Green
Write-Host "Test at: http://localhost:8080/health" -ForegroundColor Green
Write-Host "`nTo run manually: cd $apiPath; python bloomberg_api_server.py" -ForegroundColor Cyan