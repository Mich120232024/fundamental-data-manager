# Fix the volatility endpoint to handle Bloomberg errors properly

# Read current file
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Find the volatility endpoint processing section and fix it
$oldPattern = '(?s)volatility_data = \[\].*?for security, data in bloomberg_data\.items\(\):\s*volatility_data\.append\(\{\s*"security": security,.*?\}\)'

$newPattern = @'
volatility_data = []
          for security, data in bloomberg_data.items():
              if isinstance(data, dict):
                  # Data is valid
                  volatility_data.append({
                      "security": security,
                      "data": data,
                      "success": True
                  })
              else:
                  # Data is an error string
                  volatility_data.append({
                      "security": security,
                      "data": None,
                      "error": str(data),
                      "success": False
                  })
'@

$content = $content -replace $oldPattern, $newPattern

# Save the fixed file
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Fixed volatility endpoint error handling"