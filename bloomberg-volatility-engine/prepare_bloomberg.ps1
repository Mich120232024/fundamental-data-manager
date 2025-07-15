# Bloomberg Terminal System Preparation Script
# Run this directly in PowerShell on the Azure VM

Write-Host "Bloomberg Terminal System Preparation" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Create Bloomberg directory
Write-Host "`nCreating Bloomberg directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path C:\Bloomberg -Force | Out-Null
Set-Location C:\Bloomberg

# Install Chocolatey package manager
Write-Host "`nInstalling Chocolatey package manager..." -ForegroundColor Yellow
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Refresh environment
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Install Python 3.11
Write-Host "`nInstalling Python 3.11..." -ForegroundColor Yellow
choco install python311 -y --force

# Install Git (useful for downloading scripts)
Write-Host "`nInstalling Git..." -ForegroundColor Yellow
choco install git -y

# Install Visual C++ Redistributables (required by Bloomberg)
Write-Host "`nInstalling Visual C++ Redistributables..." -ForegroundColor Yellow
choco install vcredist-all -y

# Create Python script for Bloomberg API setup
Write-Host "`nCreating Bloomberg API setup script..." -ForegroundColor Yellow
$pythonScript = @'
import subprocess
import sys
import os

print("Bloomberg API Setup Script")
print("=" * 50)

# Check Python version
print(f"Python version: {sys.version}")

# Install pip if not present
print("\nUpgrading pip...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

# Install Bloomberg API
print("\nInstalling Bloomberg API...")
try:
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "--index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/",
        "blpapi"
    ])
    print("✓ Bloomberg API installed successfully!")
except Exception as e:
    print(f"✗ Failed to install Bloomberg API: {e}")
    print("\nManual installation command:")
    print("pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/ blpapi")

# Install Azure SDKs
print("\nInstalling Azure SDKs...")
packages = [
    "azure-identity",
    "azure-cosmos",
    "azure-eventhub", 
    "azure-keyvault-secrets",
    "pandas",
    "numpy",
    "python-dotenv"
]

for package in packages:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Installed {package}")
    except:
        print(f"✗ Failed to install {package}")

print("\n" + "=" * 50)
print("Setup complete!")
print("\nNext steps:")
print("1. Install Bloomberg Terminal from Bloomberg support")
print("2. After installation, run this script again to verify API")
'@

$pythonScript | Out-File -FilePath "C:\Bloomberg\setup_bloomberg_api.py" -Encoding UTF8

# Download the integration script
Write-Host "`nDownloading Bloomberg Azure integration script..." -ForegroundColor Yellow
$integrationScript = @'
# Copy the bloomberg_azure_integration.py content here
# This will be the main integration script
'@

# Enable required Windows features
Write-Host "`nEnabling .NET Framework features..." -ForegroundColor Yellow
Enable-WindowsOptionalFeature -Online -FeatureName NetFx3 -All -NoRestart
Enable-WindowsOptionalFeature -Online -FeatureName NetFx4-AdvSrvs -All -NoRestart

# Configure Windows Firewall
Write-Host "`nConfiguring Windows Firewall for Bloomberg..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Bloomberg Terminal Outbound" -Direction Outbound -Protocol TCP -RemotePort 8194,8290,8294 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Bloomberg Terminal UDP" -Direction Outbound -Protocol UDP -RemotePort 8194,8290,8294 -Action Allow -ErrorAction SilentlyContinue

Write-Host "`n" -NoNewline
Write-Host "System preparation complete!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

Write-Host "`nSystem Information:" -ForegroundColor Yellow
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture | Format-List
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory, NumberOfProcessors | Format-List

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Contact Bloomberg Support for installer:" -ForegroundColor Cyan
Write-Host "   - US: +1 212 318 2000" -ForegroundColor White
Write-Host "   - Europe: +44 20 7330 7500" -ForegroundColor White
Write-Host "   - Email: support@bloomberg.net" -ForegroundColor White
Write-Host ""
Write-Host "2. After installing Bloomberg Terminal:" -ForegroundColor Cyan
Write-Host "   python C:\Bloomberg\setup_bloomberg_api.py" -ForegroundColor White
Write-Host ""
Write-Host "3. Test Bloomberg connection:" -ForegroundColor Cyan
Write-Host "   python -c `"import blpapi; print('Bloomberg API available')`"" -ForegroundColor White