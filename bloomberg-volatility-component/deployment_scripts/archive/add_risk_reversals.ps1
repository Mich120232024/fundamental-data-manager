# Add risk reversals and butterflies back to the volatility endpoint

$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Add risk reversals and butterflies with correct format
$rrBfCode = @'
                  securities.append(f"{pair}V{tenor} BGN Curncy")
                  securities.append(f"{pair}25RR{tenor} BGN Curncy")
                  securities.append(f"{pair}25BF{tenor} BGN Curncy")
                  securities.append(f"{pair}10RR{tenor} BGN Curncy")
                  securities.append(f"{pair}10BF{tenor} BGN Curncy")
'@

# Replace the single volatility line with the full set
$content = $content -replace 'securities\.append\(f"{pair}V{tenor} BGN Curncy"\)', $rrBfCode.Trim()

# Save
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Added risk reversals and butterflies"