# Fix only the ATM volatility ticker format

$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Replace the ATM volatility ticker format
$content = $content -replace 'securities\.append\(f"{pair}{tenor} ATM Vol"\)', 'securities.append(f"{pair}V{tenor} BGN Curncy")'

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Fixed ATM volatility ticker format"