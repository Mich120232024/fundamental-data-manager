# Read the current main.py
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# The new reference endpoint with logging
$newEndpoint = @"
@app.post('/api/bloomberg/reference')
async def get_bloomberg_reference_data(request: BloombergReferenceRequest, api_key: str = Depends(validate_api_key)):
    query_id = f'reference_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    
    # Log the request
    logger.info(f'Bloomberg reference request | Securities: {len(request.securities)} | Fields: {len(request.fields)} | Query ID: {query_id}')
    
    try:
        # Log the Bloomberg request
        comprehensive_logger.log_bloomberg_request(request.securities, request.fields, query_id)
        
        bloomberg_data = bloomberg.get_reference_data(request.securities, request.fields)
        
        securities_data = []
        for security, data in bloomberg_data.items():
            if isinstance(data, dict):
                securities_data.append({
                    'security': security,
                    'fields': data,
                    'success': True
                })
            else:
                securities_data.append({
                    'security': security,
                    'fields': {},
                    'success': False,
                    'error': str(data)
                })
        
        response = {
            'success': True,
            'data': {
                'securities_data': securities_data,
                'source': 'Bloomberg Terminal'
            }
        }
        
        # Log successful response
        logger.info(f'Bloomberg reference response: {len(securities_data)} securities processed | Query ID: {query_id}')
        
        return response
        
    except Exception as e:
        # Log error
        logger.error(f'Bloomberg reference error: {str(e)} | Query ID: {query_id}')
        comprehensive_logger.log_bloomberg_error(e, 'reference_data', query_id)
        
        return {
            'success': False,
            'error': str(e)
        }
"@

# Replace the current reference endpoint (from @app.post to the end of the function)
$pattern = "@app\.post\('/api/bloomberg/reference'\)[\s\S]*?return \{\s*'success': False,\s*'error': str\(e\)\s*\}"
$content = $content -replace $pattern, $newEndpoint

# Write the updated content
$content | Set-Content 'C:\BloombergAPI\main.py'

# Restart the API server
Write-Output "Stopping existing API server..."
Get-Process python* | Stop-Process -Force

Write-Output "Starting API server with logging fix..."
Start-Sleep -Seconds 3
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden

Write-Output "API server restarted with reference endpoint logging fix"