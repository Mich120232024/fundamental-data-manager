# Final fix for volatility endpoint - use PX_LAST field

$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# 1. Fix the fields array to use PX_LAST
$content = $content -replace 'fields = \["VOLATILITY_MID", "C25R", "C25B", "C10R", "C10B"\]', 'fields = ["PX_LAST"]'

# 2. Fix the response to use PX_LAST
$content = $content -replace '"VOLATILITY_MID": data\.get\("VOLATILITY_MID"\) if isinstance\(data, dict\) else None,', '"PX_LAST": data.get("PX_LAST") if isinstance(data, dict) else None,'

# 3. Remove the other fields
$content = $content -replace '"C25R": data\.get\("C25R"\) if isinstance\(data, dict\) else None,', ''
$content = $content -replace '"C25B": data\.get\("C25B"\) if isinstance\(data, dict\) else None,', ''
$content = $content -replace '"C10R": data\.get\("C10R"\) if isinstance\(data, dict\) else None,', ''
$content = $content -replace '"C10B": data\.get\("C10B"\) if isinstance\(data, dict\) else None,', ''

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Fixed volatility endpoint to use PX_LAST field"