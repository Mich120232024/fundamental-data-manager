# Bloomberg Terminal Installation Script for Azure VM
# Run this script as Administrator on the Bloomberg VM

Write-Host "Bloomberg Terminal Installation Helper" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Step 1: Check system requirements
Write-Host "`nChecking system requirements..." -ForegroundColor Yellow
$os = Get-WmiObject -Class Win32_OperatingSystem
$cpu = Get-WmiObject -Class Win32_Processor
$memory = Get-WmiObject -Class Win32_ComputerSystem

Write-Host "OS: $($os.Caption) $($os.Version)"
Write-Host "CPU: $($cpu.Name)"
Write-Host "RAM: $([math]::Round($memory.TotalPhysicalMemory / 1GB, 2)) GB"
Write-Host "Architecture: $($cpu.AddressWidth)-bit"

# Step 2: Enable required Windows features
Write-Host "`nEnabling required Windows features..." -ForegroundColor Yellow
Enable-WindowsOptionalFeature -Online -FeatureName NetFx3 -All -NoRestart
Enable-WindowsOptionalFeature -Online -FeatureName NetFx4-AdvSrvs -All -NoRestart

# Step 3: Configure firewall rules for Bloomberg
Write-Host "`nConfiguring Windows Firewall for Bloomberg..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Bloomberg Terminal" -Direction Outbound -Protocol TCP -RemotePort 8194,8290,8294 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Bloomberg Terminal UDP" -Direction Outbound -Protocol UDP -RemotePort 8194,8290,8294 -Action Allow -ErrorAction SilentlyContinue

# Step 4: Create Bloomberg directories
Write-Host "`nCreating Bloomberg directories..." -ForegroundColor Yellow
$bloombergPath = "C:\blp"
if (!(Test-Path $bloombergPath)) {
    New-Item -ItemType Directory -Path $bloombergPath -Force
}

# Step 5: Download instructions
Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "MANUAL INSTALLATION STEPS:" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. Contact Bloomberg Support:" -ForegroundColor Cyan
Write-Host "   - Phone: +1 212 318 2000 (US)"
Write-Host "   - Phone: +44 20 7330 7500 (Europe)"
Write-Host "   - Email: support@bloomberg.net"
Write-Host ""
Write-Host "2. Request Bloomberg Terminal installation package:" -ForegroundColor Cyan
Write-Host "   - Provide your Bloomberg subscription details"
Write-Host "   - Request the Windows installer package"
Write-Host "   - Mention this is for Azure VM deployment"
Write-Host ""
Write-Host "3. Download will be provided via:" -ForegroundColor Cyan
Write-Host "   - Bloomberg Professional Service website"
Write-Host "   - Direct download link from support"
Write-Host "   - Bloomberg Anywhere if you have access"
Write-Host ""
Write-Host "4. Installation Process:" -ForegroundColor Cyan
Write-Host "   a. Run the Bloomberg installer as Administrator"
Write-Host "   b. Follow the installation wizard"
Write-Host "   c. Enter your Bloomberg login credentials"
Write-Host "   d. Complete biometric setup if required"
Write-Host ""
Write-Host "5. Post-Installation:" -ForegroundColor Cyan
Write-Host "   - Launch Bloomberg Terminal"
Write-Host "   - Complete initial setup and authentication"
Write-Host "   - Verify connection to Bloomberg servers"
Write-Host ""

# Step 6: Install Python for Bloomberg API
Write-Host "Installing Python for Bloomberg API..." -ForegroundColor Yellow
Write-Host "Downloading Python 3.11..." -ForegroundColor Yellow

# Create download directory
$downloadPath = "$env:TEMP\bloomberg_setup"
if (!(Test-Path $downloadPath)) {
    New-Item -ItemType Directory -Path $downloadPath -Force
}

# Download Python installer
$pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
$pythonInstaller = "$downloadPath\python-3.11.8-amd64.exe"

try {
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    Write-Host "Python downloaded successfully" -ForegroundColor Green
    
    # Install Python silently
    Write-Host "Installing Python..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
    
    Write-Host "Python installation completed" -ForegroundColor Green
} catch {
    Write-Host "Failed to download/install Python. Please install manually from python.org" -ForegroundColor Red
}

# Step 7: Create Bloomberg API setup script
$apiSetupScript = @'
# Bloomberg API Setup Script
import subprocess
import sys

print("Setting up Bloomberg Python API...")

# Install blpapi
try:
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "--index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/", 
        "blpapi"
    ])
    print("Bloomberg API installed successfully!")
except Exception as e:
    print(f"Failed to install Bloomberg API: {e}")
    print("Please run manually: pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/ blpapi")

# Install Azure SDK
print("\nInstalling Azure SDK...")
packages = [
    "azure-identity",
    "azure-cosmos", 
    "azure-eventhub",
    "azure-keyvault-secrets",
    "pandas",
    "numpy"
]

for package in packages:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Installed {package}")
    except:
        print(f"Failed to install {package}")

print("\nSetup complete!")
'@

$apiSetupScript | Out-File -FilePath "$bloombergPath\setup_bloomberg_api.py" -Encoding UTF8

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "System prepared for Bloomberg Terminal" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Contact Bloomberg Support for installation package" -ForegroundColor White
Write-Host "2. Run the Bloomberg installer when received" -ForegroundColor White
Write-Host "3. After Bloomberg installation, run: python C:\blp\setup_bloomberg_api.py" -ForegroundColor White
Write-Host ""
Write-Host "VM Connection Details:" -ForegroundColor Yellow
Write-Host "Server: 172.171.211.16" -ForegroundColor White
Write-Host "Username: bloombergadmin" -ForegroundColor White
Write-Host ""