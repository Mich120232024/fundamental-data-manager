# PowerShell deployment script for Bloomberg API Server v2

Write-Host "Deploying Bloomberg API Server v2..." -ForegroundColor Cyan

# Stop any existing processes
Get-Process python* -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*python*" 
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Stopped existing Python processes"

# Wait a moment
Start-Sleep -Seconds 3

# Create directory if needed
New-Item -ItemType Directory -Force -Path "C:\Bloomberg\APIServer" | Out-Null

# Copy the new API server
$apiServerContent = @'
[CONTENT_PLACEHOLDER]
'@

# The content will be inserted here during deployment
$apiServerContent | Out-File -FilePath "C:\Bloomberg\APIServer\bloomberg_api_server_v2.py" -Encoding UTF8

# Start the new server
Write-Host "Starting new API server..."
cd C:\Bloomberg\APIServer

# Start as background job
Start-Job -Name "BloombergAPI" -ScriptBlock {
    Set-Location "C:\Bloomberg\APIServer"
    & "C:\Python311\python.exe" "bloomberg_api_server_v2.py"
} | Out-Null

Write-Host "API server started as background job"

# Wait for initialization
Start-Sleep -Seconds 5

# Test the server
$testUrl = "http://localhost:8080/api/health"
try {
    $response = Invoke-RestMethod -Uri $testUrl -Method Get
    Write-Host "✓ API Server is running!" -ForegroundColor Green
    Write-Host "  Bloomberg connected: $($response.bloomberg_connected)" -ForegroundColor Green
    Write-Host "  Version: $($response.version)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ API Server is starting up..." -ForegroundColor Yellow
    Write-Host "  Check http://localhost:8080/api/health in a few seconds"
}

Write-Host "`nDeployment complete!" -ForegroundColor Green