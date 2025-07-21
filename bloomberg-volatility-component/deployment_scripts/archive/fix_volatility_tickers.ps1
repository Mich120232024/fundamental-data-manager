# Fix volatility ticker format to use correct Bloomberg format

# Read current file
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Find and replace the ticker construction
$oldPattern = 'securities.append\(f"{pair}{tenor} ATM Vol"\)'
$newPattern = 'securities.append(f"{pair}V{tenor} BGN Curncy")'

$content = $content -replace [regex]::Escape($oldPattern), $newPattern

# Also fix the other ticker formats (Risk Reversals and Butterflies)
$content = $content -replace 'securities\.append\(f"{pair}{tenor} 25D RR"\)', '# securities.append(f"{pair}25RR{tenor} BGN Curncy")'
$content = $content -replace 'securities\.append\(f"{pair}{tenor} 25D BF"\)', '# securities.append(f"{pair}25BF{tenor} BGN Curncy")'
$content = $content -replace 'securities\.append\(f"{pair}{tenor} 10D RR"\)', '# securities.append(f"{pair}10RR{tenor} BGN Curncy")'
$content = $content -replace 'securities\.append\(f"{pair}{tenor} 10D BF"\)', '# securities.append(f"{pair}10BF{tenor} BGN Curncy")'

# Fix the fields to use PX_LAST
$content = $content -replace 'fields = \["VOLATILITY_MID", "C25R", "C25B", "C10R", "C10B"\]', 'fields = ["PX_LAST"]'

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Fixed volatility ticker formats"