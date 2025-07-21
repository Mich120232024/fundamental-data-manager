# Fix all ticker formats using documented correct formats

$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Replace entire securities construction section with correct formats
$securitiesSection = @'
          # Build Bloomberg securities using documented correct formats
          securities = []
          for pair in request.currency_pairs:
              for tenor in request.tenors:
                  # ATM Volatility - CORRECT FORMAT
                  securities.append(f"{pair}V{tenor} BGN Curncy")
                  
                  # Risk Reversals - CORRECT FORMAT
                  securities.append(f"{pair}10RR{tenor} BGN Curncy")
                  securities.append(f"{pair}25RR{tenor} BGN Curncy")
                  
                  # Butterflies - CORRECT FORMAT
                  securities.append(f"{pair}10BF{tenor} BGN Curncy")
                  securities.append(f"{pair}25BF{tenor} BGN Curncy")
'@

# Find and replace the securities construction
$pattern = '(?s)# Build Bloomberg securities.*?securities\.append\(f"{pair}{tenor} 10D BF"\)'
$content = $content -replace $pattern, $securitiesSection.Trim()

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Fixed all ticker formats to use documented correct formats"