# Simple approach - just enable the import blpapi line

# Backup
Copy-Item 'C:\BloombergAPI\main.py' 'C:\BloombergAPI\main_backup_before_import.py'

# Read file
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Uncomment the import blpapi line
$content = $content -replace '# import blpapi', 'import blpapi'

# Remove the hardcoded exception after import
$content = $content -replace 'raise Exception\("Bloomberg API not available - blpapi package not installed"\)', '# Bloomberg is now available'

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Enabled blpapi import"