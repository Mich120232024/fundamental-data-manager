# PowerShell script to run on the Bloomberg VM
# This will start the API server and keep it running

Write-Host "Starting Bloomberg API Server with auto-restart..." -ForegroundColor Green

# Kill any existing Python processes running the API
Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*bloomberg_api_server*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Function to start the API server
function Start-BloombergAPI {
    $scriptBlock = {
        Set-Location "C:\Bloomberg\APIServer"
        & "C:\Python311\python.exe" "bloomberg_api_server.py"
    }
    
    Start-Job -Name "BloombergAPI" -ScriptBlock $scriptBlock
}

# Start the API
Start-BloombergAPI

Write-Host "API Server started as background job" -ForegroundColor Green
Write-Host "Waiting for it to initialize..." -ForegroundColor Yellow

Start-Sleep -Seconds 5

# Test if it's running
$testUrl = "http://localhost:8080/api/health"
try {
    $response = Invoke-RestMethod -Uri $testUrl
    Write-Host "✓ API Server is running!" -ForegroundColor Green
    Write-Host "  Bloomberg connected: $($response.bloomberg_connected)" -ForegroundColor Green
    Write-Host "  Access it at: http://localhost:8080" -ForegroundColor Cyan
} catch {
    Write-Host "API Server is still starting, check in a few seconds..." -ForegroundColor Yellow
}

Write-Host "`nTo check API status later, run:" -ForegroundColor Cyan
Write-Host "  Get-Job -Name BloombergAPI" -ForegroundColor White
Write-Host "  Invoke-RestMethod http://localhost:8080/api/health" -ForegroundColor White