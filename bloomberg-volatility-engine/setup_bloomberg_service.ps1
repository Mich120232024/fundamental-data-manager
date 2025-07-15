# Setup Bloomberg API Server as Windows Service
# Run this on the Bloomberg VM to install the API server

Write-Host "Bloomberg API Server Setup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script must be run as Administrator!" -ForegroundColor Red
    exit 1
}

# Set paths
$installPath = "C:\Bloomberg\APIServer"
$pythonPath = "C:\Python311\python.exe"
$pipPath = "C:\Python311\Scripts\pip.exe"

# Create directory
Write-Host "`nCreating installation directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $installPath | Out-Null

# Copy server file (you'll need to transfer this)
Write-Host "Please copy bloomberg_api_server.py to $installPath" -ForegroundColor Yellow

# Install required packages
Write-Host "`nInstalling required Python packages..." -ForegroundColor Yellow
& $pipPath install fastapi uvicorn[standard] python-multipart azure-identity azure-cosmos azure-eventhub

# Create a startup script
$startupScript = @"
@echo off
cd /d C:\Bloomberg\APIServer
C:\Python311\python.exe bloomberg_api_server.py
"@

$startupScript | Out-File -FilePath "$installPath\start_server.bat" -Encoding ASCII

# Create Windows Task Scheduler task to run at startup
Write-Host "`nCreating Windows Task Scheduler task..." -ForegroundColor Yellow

$action = New-ScheduledTaskAction -Execute "$installPath\start_server.bat"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartInterval (New-TimeSpan -Minutes 1) -RestartCount 3

Register-ScheduledTask -TaskName "BloombergAPIServer" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force

Write-Host "`nConfiguring Windows Firewall..." -ForegroundColor Yellow
# Open port 8080 for the API server
New-NetFirewallRule -DisplayName "Bloomberg API Server" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Any

Write-Host "`nStarting Bloomberg API Server..." -ForegroundColor Yellow
Start-ScheduledTask -TaskName "BloombergAPIServer"

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "Bloomberg API Server will run on port 8080" -ForegroundColor Green
Write-Host "Access it at: http://${env:COMPUTERNAME}:8080 or http://localhost:8080" -ForegroundColor Green
Write-Host "`nAPI Documentation available at: http://localhost:8080/docs" -ForegroundColor Cyan