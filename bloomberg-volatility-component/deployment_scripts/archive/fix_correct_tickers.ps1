# Fix ticker formats to use correct Bloomberg volatility format

$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Replace the old ticker construction with correct Bloomberg format
$content = $content -replace 'securities\.append\(f"{pair}{tenor} ATM Vol"\)', 'securities.append(f"{pair}V{tenor} BGN Curncy")'

# Update the fields to use PX_LAST instead of VOLATILITY_MID
$content = $content -replace 'fields = \["VOLATILITY_MID", "C25R", "C25B", "C10R", "C10B"\]', 'fields = ["PX_LAST"]'

# Update the response processing to use PX_LAST
$content = $content -replace '"VOLATILITY_MID": data\.get\("VOLATILITY_MID"\) if isinstance\(data, dict\) else None,', '"PX_LAST": data.get("PX_LAST") if isinstance(data, dict) else None,'
$content = $content -replace '"C25R": data\.get\("C25R"\) if isinstance\(data, dict\) else None,', ''
$content = $content -replace '"C25B": data\.get\("C25B"\) if isinstance\(data, dict\) else None,', ''
$content = $content -replace '"C10R": data\.get\("C10R"\) if isinstance\(data, dict\) else None,', ''
$content = $content -replace '"C10B": data\.get\("C10B"\) if isinstance\(data, dict\) else None,', ''

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Fixed ticker formats to use correct Bloomberg volatility format"