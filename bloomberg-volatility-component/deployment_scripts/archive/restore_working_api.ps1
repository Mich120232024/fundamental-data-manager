# Restart the API server to the last working state
Write-Output "Restoring API to last working state..."

# Backup the current file
Copy-Item 'C:\BloombergAPI\main.py' 'C:\BloombergAPI\main_backup.py'

# Remove the broken historical method addition
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Remove everything we added for historical (from the historical method to the end)
# This will restore to the working reference endpoint state
$pattern = "def get_historical_data.*?bloomberg = BloombergSession\(\)"
$content = $content -replace $pattern, "bloomberg = BloombergSession()", "Singleline"

# Also remove the historical endpoint if it was added
$pattern = "class BloombergHistoricalRequest.*?if __name__ == `"__main__`":"
$content = $content -replace $pattern, 'if __name__ == "__main__":', "Singleline"

# Write the cleaned content
$content | Set-Content 'C:\BloombergAPI\main.py'

# Start the API server
Write-Output "Starting API server in working state..."
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden

Write-Output "API server restored to working state"