# 🚨 GEMINI CLI SETUP FOR BLOOMBERG VM - CURSOR MAILBOX

**Location**: Copy this to `C:\Users\bloombergadmin\.cursor\Mailbox\Gemini-Setup\`  
**Purpose**: Fix Gemini CLI credential issues on Bloomberg VM  
**Date**: 2025-07-13

## 📋 PROBLEM SUMMARY

The Gemini CLI on the Bloomberg VM is not recognizing credentials/API key. This document provides a complete solution.

## 🔑 API KEY INFORMATION

```
GEMINI_API_KEY: AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4
```

This API key is already working on the Mac system in Claude Router configuration.

## 🚀 QUICK FIX STEPS

### Option 1: PowerShell Environment Variable (Fastest)

Open PowerShell on Bloomberg VM and run:

```powershell
# Set for current session
$env:GEMINI_API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"

# Set permanently for user
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4", "User")

# Test immediately
gemini "Hello, are you working?"
```

### Option 2: Create Config Files

Create these configuration files on the Bloomberg VM:

1. **Primary Config**: `C:\Users\bloombergadmin\.gemini\config.json`
```json
{
  "api_key": "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4",
  "default_model": "gemini-pro",
  "region": "us-central1"
}
```

2. **Alternative Config**: `C:\Users\bloombergadmin\.config\gemini\config.json`
```json
{
  "api_key": "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4",
  "default_model": "gemini-pro",
  "region": "us-central1"
}
```

3. **AppData Config**: `C:\Users\bloombergadmin\AppData\Roaming\gemini\config.json`
```json
{
  "api_key": "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4",
  "default_model": "gemini-pro",
  "region": "us-central1"
}
```

## 🛠️ COMPLETE SETUP SCRIPT

Save this as `setup_gemini.ps1` and run in PowerShell:

```powershell
# Gemini CLI Setup Script
Write-Host "Setting up Gemini CLI..." -ForegroundColor Green

$API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"

# Set environment variable
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $API_KEY, "User")
$env:GEMINI_API_KEY = $API_KEY

# Create all config directories
$dirs = @(
    "$env:USERPROFILE\.gemini",
    "$env:USERPROFILE\.config\gemini",
    "$env:APPDATA\gemini"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Yellow
    }
}

# Create config content
$config = @{
    api_key = $API_KEY
    default_model = "gemini-pro"
    region = "us-central1"
} | ConvertTo-Json

# Write config files
$configPaths = @(
    "$env:USERPROFILE\.gemini\config.json",
    "$env:USERPROFILE\.config\gemini\config.json",
    "$env:APPDATA\gemini\config.json"
)

foreach ($path in $configPaths) {
    $config | Out-File -FilePath $path -Encoding UTF8 -Force
    Write-Host "Config created: $path" -ForegroundColor Green
}

Write-Host "`nSetup complete! Test with: gemini 'Hello world'" -ForegroundColor Green
```

## 🐍 PYTHON FALLBACK (IF CLI FAILS)

If Gemini CLI continues to fail, use Python SDK:

1. **Install Package**:
```bash
pip install google-generativeai
```

2. **Test Script** (`test_gemini.py`):
```python
import google.generativeai as genai

# Configure
genai.configure(api_key="AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4")

# Test
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello, confirm you're working")
print(response.text)
```

3. **Simple CLI Wrapper** (`gemini-wrapper.py`):
```python
#!/usr/bin/env python
import sys
import google.generativeai as genai

genai.configure(api_key="AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4")

if len(sys.argv) < 2:
    print("Usage: python gemini-wrapper.py 'Your prompt'")
    sys.exit(1)

prompt = " ".join(sys.argv[1:])
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content(prompt)
print(response.text)
```

Usage: `python gemini-wrapper.py "What is the weather like?"`

## 🔍 TROUBLESHOOTING

### Check if Gemini CLI is installed:
```powershell
# Check if gemini command exists
where gemini

# If not found, check gcloud
where gcloud

# List gcloud components
gcloud components list
```

### Verify Environment Variable:
```powershell
# Check if set
echo $env:GEMINI_API_KEY

# List all environment variables
Get-ChildItem Env: | Where-Object {$_.Name -like "*GEMINI*"}
```

### Test API Connection:
```powershell
# Direct API test with curl
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4" `
  -H "Content-Type: application/json" `
  -d '{\"contents\":[{\"parts\":[{\"text\":\"Hello\"}]}]}'
```

### Common Issues:

1. **"gemini: command not found"**
   - Install Google Cloud SDK first
   - Or use the Python fallback method

2. **"API key not set"**
   - Run the setup script above
   - Restart PowerShell after setting env vars

3. **Network/Firewall errors**
   - Check if `generativelanguage.googleapis.com` is accessible
   - May need proxy configuration

## 📊 INTEGRATION WITH BLOOMBERG DATA

Once Gemini is working, integrate with Bloomberg Terminal data:

```python
# bloomberg_gemini_analysis.py
import google.generativeai as genai
import json

# Configure Gemini
genai.configure(api_key="AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4")
model = genai.GenerativeModel('gemini-pro')

# Your Bloomberg data (example)
bloomberg_data = {
    "EURUSDV1M": 8.760,  # Real Terminal value
    "EUR25R1M": -0.548,
    "EUR25B1M": 0.319,
    "timestamp": "2025-07-13T10:30:00Z"
}

# Analyze with Gemini
prompt = f"""
Analyze this Bloomberg FX volatility data and provide insights:
{json.dumps(bloomberg_data, indent=2)}

Focus on:
1. Market sentiment implications
2. Trading opportunities
3. Risk considerations
"""

response = model.generate_content(prompt)
print("Gemini Analysis:")
print(response.text)
```

## ✅ VERIFICATION CHECKLIST

After setup, verify everything works:

- [ ] Environment variable is set: `echo $env:GEMINI_API_KEY`
- [ ] Config files exist in all 3 locations
- [ ] Gemini CLI works: `gemini "test"`
- [ ] Python SDK works: `python test_gemini.py`
- [ ] Can analyze Bloomberg data with Gemini

## 📝 NOTES FOR CURSOR AI

This setup ensures Gemini CLI/SDK can be used for:
1. Analyzing Bloomberg Terminal data discrepancies
2. Generating trading insights from real-time data
3. Debugging API vs Terminal value mismatches
4. Creating financial analysis reports

The API key provided is valid and working on the Mac system, so it should work on the Bloomberg VM once properly configured.

## 🆘 SUPPORT

If issues persist:
1. Check Windows Event Viewer for errors
2. Verify internet connectivity from VM
3. Try Python SDK as primary method
4. Check if corporate firewall blocks Google APIs

—SOFTWARE_RESEARCH_ANALYST