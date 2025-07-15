# Bloomberg API Server Startup and Monitoring Script
# Run this on the Bloomberg VM to ensure API server stays running

# Configuration
$apiServerPath = "C:\Bloomberg\APIServer"
$pythonExe = "C:\Python311\python.exe"
$apiScript = "real_bloomberg_api.py"
$logFile = "C:\Bloomberg\APIServer\monitor.log"
$checkInterval = 300  # Check every 5 minutes

# Function to write log
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -Append -FilePath $logFile
    Write-Host "$timestamp - $Message"
}

# Function to check if API is responding
function Test-APIHealth {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method Get -TimeoutSec 10
        return $response.bloomberg_connected -eq $true
    } catch {
        return $false
    }
}

# Function to start API server
function Start-APIServer {
    Write-Log "Starting Bloomberg API Server..."
    
    # Kill any existing Python processes
    Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Start the API server
    $process = Start-Process -FilePath $pythonExe -ArgumentList "$apiServerPath\$apiScript" -WorkingDirectory $apiServerPath -PassThru -WindowStyle Hidden
    
    Write-Log "API Server started with PID: $($process.Id)"
    
    # Wait for it to initialize
    Start-Sleep -Seconds 10
    
    # Check if it's running
    if (Test-APIHealth) {
        Write-Log "API Server is healthy and Bloomberg is connected"
        return $true
    } else {
        Write-Log "API Server failed to start properly"
        return $false
    }
}

# Function to monitor and restart if needed
function Monitor-APIServer {
    Write-Log "Starting API Server Monitor"
    
    while ($true) {
        if (-not (Test-APIHealth)) {
            Write-Log "API Server is not responding, attempting restart..."
            
            if (Start-APIServer) {
                Write-Log "API Server successfully restarted"
            } else {
                Write-Log "Failed to restart API Server - will retry in $checkInterval seconds"
            }
        } else {
            Write-Log "API Server health check passed"
        }
        
        # Wait before next check
        Start-Sleep -Seconds $checkInterval
    }
}

# Create log directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $apiServerPath | Out-Null

Write-Log "Bloomberg API Server Monitor Starting..."

# Initial start
if (-not (Test-APIHealth)) {
    Start-APIServer
}

# Start monitoring
Monitor-APIServer