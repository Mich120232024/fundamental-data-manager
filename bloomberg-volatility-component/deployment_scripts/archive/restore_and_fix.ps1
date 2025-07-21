# Restore backup and manually add endpoint

# 1. Restore from backup
Copy-Item 'C:\BloombergAPI\main_backup_deploy.py' 'C:\BloombergAPI\main.py' -Force

Write-Output "File restored from backup"

# 2. Start the API
Get-Process python* | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden

Write-Output "API restarted with original code"