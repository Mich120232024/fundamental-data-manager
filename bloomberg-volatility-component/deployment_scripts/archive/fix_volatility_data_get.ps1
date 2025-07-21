# Fix the exact line that's causing the error

$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Replace the problematic data.get() calls with proper error handling
$content = $content -replace '"VOLATILITY_MID": data\.get\("VOLATILITY_MID"\),', '"VOLATILITY_MID": data.get("VOLATILITY_MID") if isinstance(data, dict) else None,'
$content = $content -replace '"C25R": data\.get\("C25R"\),', '"C25R": data.get("C25R") if isinstance(data, dict) else None,'
$content = $content -replace '"C25B": data\.get\("C25B"\),', '"C25B": data.get("C25B") if isinstance(data, dict) else None,'
$content = $content -replace '"C10R": data\.get\("C10R"\),', '"C10R": data.get("C10R") if isinstance(data, dict) else None,'
$content = $content -replace '"C10B": data\.get\("C10B"\)', '"C10B": data.get("C10B") if isinstance(data, dict) else None,
                  "error": str(data) if not isinstance(data, dict) else None'

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Fixed volatility data.get() calls"