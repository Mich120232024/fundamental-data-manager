# GEMINI CLI SETUP FOR BLOOMBERG VM

**Location**: C:\Users\bloombergadmin\.cursor\Mailbox\Gemini-Setup\
**Issue**: Gemini CLI not recognizing credentials/API key
**Solution**: Complete setup guide with working API key

## QUICK FIX - COPY & PASTE THIS

Open PowerShell and run:

```powershell
# Set API key for current session
$env:GEMINI_API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"

# Set API key permanently
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4", "User")

# Test
gemini "Hello, are you working?"
```

## FULL SETUP SCRIPT

Save as `setup_gemini.ps1`:

```powershell
Write-Host "=== Gemini Setup ===" -ForegroundColor Green

$API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"

# Set environment variable
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $API_KEY, "User")
$env:GEMINI_API_KEY = $API_KEY

# Create config directories
$dirs = @(
    "$env:USERPROFILE\.gemini",
    "$env:USERPROFILE\.config\gemini",
    "$env:APPDATA\gemini"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Create config
$config = @{
    api_key = $API_KEY
    default_model = "gemini-pro"
} | ConvertTo-Json

# Write configs
@(
    "$env:USERPROFILE\.gemini\config.json",
    "$env:USERPROFILE\.config\gemini\config.json",
    "$env:APPDATA\gemini\config.json"
) | ForEach-Object {
    $config | Out-File -FilePath $_ -Encoding UTF8 -Force
    Write-Host "Created: $_" -ForegroundColor Green
}

Write-Host "Setup complete!" -ForegroundColor Green
```

## PYTHON FALLBACK

If CLI fails, use Python:

```python
import google.generativeai as genai

genai.configure(api_key="AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4")
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Your prompt here")
print(response.text)
```

## TEST CONNECTION

```powershell
# Test in PowerShell
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4" -H "Content-Type: application/json" -d '{\"contents\":[{\"parts\":[{\"text\":\"Hello\"}]}]}'
```

—SOFTWARE_RESEARCH_ANALYST