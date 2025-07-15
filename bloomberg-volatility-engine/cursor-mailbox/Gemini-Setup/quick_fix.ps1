# Quick Gemini Fix - Run this in PowerShell on Bloomberg VM
$env:GEMINI_API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4", "User")
Write-Host "Gemini API key configured!" -ForegroundColor Green
Write-Host "Test with: gemini 'Hello world'" -ForegroundColor Yellow