# Minimal fix - just change the ATM ticker format to working format

$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Simple replacement of ATM ticker format only
$content = $content -replace 'f"{pair}{tenor} ATM Vol"', 'f"{pair}V{tenor} BGN Curncy"'

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Applied minimal ticker fix for ATM volatility"