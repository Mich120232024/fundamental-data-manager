# Add all delta strikes with bid/ask data for volatility endpoint

$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Replace the securities construction with comprehensive delta coverage
$newSecuritiesCode = @'
          securities = []
          for pair in request.currency_pairs:
              for tenor in request.tenors:
                  # ATM volatility
                  securities.append(f"{pair}V{tenor} BGN Curncy")
                  
                  # Risk Reversals - all deltas
                  securities.append(f"{pair}5RR{tenor} BGN Curncy")
                  securities.append(f"{pair}10RR{tenor} BGN Curncy")
                  securities.append(f"{pair}15RR{tenor} BGN Curncy")
                  securities.append(f"{pair}25RR{tenor} BGN Curncy")
                  securities.append(f"{pair}35RR{tenor} BGN Curncy")
                  
                  # Butterflies - all deltas
                  securities.append(f"{pair}5BF{tenor} BGN Curncy")
                  securities.append(f"{pair}10BF{tenor} BGN Curncy")
                  securities.append(f"{pair}15BF{tenor} BGN Curncy")
                  securities.append(f"{pair}25BF{tenor} BGN Curncy")
                  securities.append(f"{pair}35BF{tenor} BGN Curncy")
'@

# Find and replace the securities construction section
$pattern = '(?s)securities = \[\].*?for tenor in request\.tenors:.*?securities\.append\(f"{pair}{tenor} 10D BF"\)'
$content = $content -replace $pattern, $newSecuritiesCode.Trim()

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Added all delta strikes (5D, 10D, 15D, 25D, 35D) with bid/ask support"