# Fix the logger references in the reference endpoint
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Replace comprehensive_logger with logger
$content = $content -replace 'comprehensive_logger\.log_bloomberg_request\(request\.securities, request\.fields, query_id\)', 'logger.info(f"Bloomberg request - Securities: {request.securities} | Fields: {request.fields} | Query ID: {query_id}")'

$content = $content -replace 'comprehensive_logger\.log_bloomberg_error\(e, ''reference_data'', query_id\)', 'logger.error(f"Bloomberg error: {str(e)} | Query ID: {query_id}")'

# Write the fixed content
$content | Set-Content 'C:\BloombergAPI\main.py'

# Restart the API server
Write-Output "Stopping existing API server..."
Get-Process python* | Stop-Process -Force

Write-Output "Starting API server with logger fix..."
Start-Sleep -Seconds 3
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden

Write-Output "API server restarted with logger fix"