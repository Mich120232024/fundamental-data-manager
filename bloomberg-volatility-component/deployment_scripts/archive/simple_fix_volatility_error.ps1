# Simple fix for the volatility endpoint error handling

$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Find and replace the problematic line that tries to call .get() on a string
$content = $content -replace 'volatility_data\.append\(\{\s*"security": security,\s*"data": data\.get\("PX_LAST"\),', 'volatility_data.append({
                      "security": security,
                      "data": data.get("PX_LAST") if isinstance(data, dict) else None,
                      "error": str(data) if not isinstance(data, dict) else None,'

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Fixed volatility endpoint error handling"