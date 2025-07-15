# PowerShell script to set up Gemini CLI on Bloomberg VM
# Run this script on the Bloomberg VM as Administrator

Write-Host "=== Gemini CLI Setup for Bloomberg VM ===" -ForegroundColor Green
Write-Host "Setting up Gemini CLI with proper credentials..." -ForegroundColor Yellow

# API Key from Claude Router configuration
$GEMINI_API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"

# Step 1: Set Environment Variable (User level - permanent)
Write-Host "`n[1/5] Setting GEMINI_API_KEY environment variable..." -ForegroundColor Cyan
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $GEMINI_API_KEY, "User")
$env:GEMINI_API_KEY = $GEMINI_API_KEY
Write-Host "✓ Environment variable set successfully" -ForegroundColor Green

# Step 2: Create Gemini configuration directory
Write-Host "`n[2/5] Creating Gemini configuration directory..." -ForegroundColor Cyan
$geminiDir = "$env:USERPROFILE\.gemini"
if (-not (Test-Path $geminiDir)) {
    New-Item -ItemType Directory -Path $geminiDir -Force | Out-Null
    Write-Host "✓ Created directory: $geminiDir" -ForegroundColor Green
} else {
    Write-Host "✓ Directory already exists: $geminiDir" -ForegroundColor Green
}

# Step 3: Create configuration file
Write-Host "`n[3/5] Creating Gemini configuration file..." -ForegroundColor Cyan
$configContent = @{
    api_key = $GEMINI_API_KEY
    default_model = "gemini-pro"
    region = "us-central1"
} | ConvertTo-Json -Depth 10

$configPath = "$geminiDir\config.json"
$configContent | Out-File -FilePath $configPath -Encoding UTF8 -Force
Write-Host "✓ Configuration file created: $configPath" -ForegroundColor Green

# Step 4: Create alternative config locations (some CLI versions check different paths)
Write-Host "`n[4/5] Creating alternative configuration locations..." -ForegroundColor Cyan

# .config/gemini directory
$altConfigDir1 = "$env:USERPROFILE\.config\gemini"
if (-not (Test-Path $altConfigDir1)) {
    New-Item -ItemType Directory -Path $altConfigDir1 -Force | Out-Null
}
$configContent | Out-File -FilePath "$altConfigDir1\config.json" -Encoding UTF8 -Force
Write-Host "✓ Alternative config created: $altConfigDir1\config.json" -ForegroundColor Green

# AppData/Roaming location
$altConfigDir2 = "$env:APPDATA\gemini"
if (-not (Test-Path $altConfigDir2)) {
    New-Item -ItemType Directory -Path $altConfigDir2 -Force | Out-Null
}
$configContent | Out-File -FilePath "$altConfigDir2\config.json" -Encoding UTF8 -Force
Write-Host "✓ Alternative config created: $altConfigDir2\config.json" -ForegroundColor Green

# Step 5: Display current configuration
Write-Host "`n[5/5] Verifying configuration..." -ForegroundColor Cyan
Write-Host "Environment Variable GEMINI_API_KEY: $($env:GEMINI_API_KEY.Substring(0,10))..." -ForegroundColor Yellow
Write-Host "Config files created in:" -ForegroundColor Yellow
Write-Host "  - $geminiDir\config.json" -ForegroundColor Gray
Write-Host "  - $altConfigDir1\config.json" -ForegroundColor Gray
Write-Host "  - $altConfigDir2\config.json" -ForegroundColor Gray

# Final instructions
Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "`nTo verify Gemini CLI is working, run:" -ForegroundColor Yellow
Write-Host "  gemini --version" -ForegroundColor Cyan
Write-Host "  gemini 'Hello, test message'" -ForegroundColor Cyan
Write-Host "`nIf Gemini CLI is not installed, download it from:" -ForegroundColor Yellow
Write-Host "  https://cloud.google.com/sdk/docs/install" -ForegroundColor Cyan

# Create a test script
$testScript = @'
# Test Gemini CLI connection
Write-Host "Testing Gemini CLI..." -ForegroundColor Yellow
try {
    $result = gemini "What is 2+2?" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Gemini CLI is working!" -ForegroundColor Green
        Write-Host "Response: $result" -ForegroundColor Cyan
    } else {
        Write-Host "✗ Gemini CLI test failed" -ForegroundColor Red
        Write-Host "Error: $result" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Gemini CLI not found or error occurred" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
'@

$testScriptPath = "$env:USERPROFILE\Desktop\test_gemini.ps1"
$testScript | Out-File -FilePath $testScriptPath -Encoding UTF8
Write-Host "`nTest script created on Desktop: test_gemini.ps1" -ForegroundColor Green