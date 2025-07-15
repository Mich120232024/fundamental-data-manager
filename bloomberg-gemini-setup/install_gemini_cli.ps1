# Install Google Cloud SDK (includes Gemini CLI) on Windows
# Run this as Administrator on Bloomberg VM

Write-Host "=== Google Cloud SDK Installation Script ===" -ForegroundColor Green
Write-Host "This will install the Google Cloud SDK which includes Gemini CLI" -ForegroundColor Yellow

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Step 1: Download Google Cloud SDK installer
Write-Host "`n[1/4] Downloading Google Cloud SDK installer..." -ForegroundColor Cyan
$installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
$installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"

try {
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✓ Downloaded installer successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to download installer" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Install Google Cloud SDK
Write-Host "`n[2/4] Installing Google Cloud SDK..." -ForegroundColor Cyan
Write-Host "This will open the installer. Please follow these steps:" -ForegroundColor Yellow
Write-Host "1. Click 'Next' through the installation wizard" -ForegroundColor Gray
Write-Host "2. Accept the license agreement" -ForegroundColor Gray
Write-Host "3. Choose installation location (default is fine)" -ForegroundColor Gray
Write-Host "4. UNCHECK 'Start Google Cloud SDK Shell' at the end" -ForegroundColor Gray
Write-Host "5. Click 'Finish'" -ForegroundColor Gray

# Start the installer
Start-Process -FilePath $installerPath -Wait

# Step 3: Add to PATH if not already there
Write-Host "`n[3/4] Updating system PATH..." -ForegroundColor Cyan
$gcloudPath = "${env:ProgramFiles(x86)}\Google\Cloud SDK\google-cloud-sdk\bin"
if (-not (Test-Path $gcloudPath)) {
    $gcloudPath = "$env:ProgramFiles\Google\Cloud SDK\google-cloud-sdk\bin"
}

if (Test-Path $gcloudPath) {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$gcloudPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gcloudPath", "Machine")
        Write-Host "✓ Added Google Cloud SDK to system PATH" -ForegroundColor Green
    } else {
        Write-Host "✓ Google Cloud SDK already in PATH" -ForegroundColor Green
    }
    
    # Update current session PATH
    $env:Path = "$env:Path;$gcloudPath"
} else {
    Write-Host "✗ Could not find Google Cloud SDK installation" -ForegroundColor Red
    Write-Host "Please check if installation completed successfully" -ForegroundColor Yellow
}

# Step 4: Initialize gcloud with minimal config
Write-Host "`n[4/4] Initializing gcloud configuration..." -ForegroundColor Cyan

# Create a batch file to run gcloud commands
$initScript = @'
@echo off
echo Initializing gcloud configuration...
call gcloud config set disable_usage_reporting true
call gcloud config set component_manager_disable_update_check true
call gcloud config set core/disable_prompts true
echo Configuration complete!
'@

$initScriptPath = "$env:TEMP\init_gcloud.bat"
$initScript | Out-File -FilePath $initScriptPath -Encoding ASCII
Start-Process -FilePath "cmd.exe" -ArgumentList "/c $initScriptPath" -Wait

# Cleanup
Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
Remove-Item $initScriptPath -Force -ErrorAction SilentlyContinue

# Final message
Write-Host "`n=== Installation Complete ===" -ForegroundColor Green
Write-Host "`nIMPORTANT: You need to restart your PowerShell/Command Prompt for PATH changes to take effect!" -ForegroundColor Yellow
Write-Host "`nAfter restarting, verify installation with:" -ForegroundColor Cyan
Write-Host "  gcloud --version" -ForegroundColor Gray
Write-Host "  gcloud ai models list --region=us-central1" -ForegroundColor Gray
Write-Host "`nThen run the setup_gemini_bloomberg_vm.ps1 script to configure Gemini API key" -ForegroundColor Yellow