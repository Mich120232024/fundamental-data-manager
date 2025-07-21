# Read the current main.py
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Historical request model and endpoint
$historicalEndpoint = @"

# Historical Bloomberg Data Request Model
class BloombergHistoricalRequest(BaseModel):
    security: str
    fields: List[str]
    start_date: str  # YYYYMMDD format
    end_date: str    # YYYYMMDD format
    periodicity: str = "DAILY"  # DAILY, WEEKLY, MONTHLY

@app.post('/api/bloomberg/historical')
async def get_bloomberg_historical_data(
    request: BloombergHistoricalRequest, 
    api_key: str = Depends(validate_api_key)
):
    `"``"``"Bloomberg historical data endpoint`"``"``"
    query_id = f'historical_{datetime.now().strftime(`"%Y%m%d_%H%M%S_%f`")}'
    
    # Log the request
    logger.info(f'Bloomberg historical request | Security: {request.security} | Fields: {len(request.fields)} | Date range: {request.start_date} to {request.end_date} | Query ID: {query_id}')
    
    try:
        # Log the Bloomberg request
        logger.info(f'Bloomberg historical request - Security: {request.security} | Fields: {request.fields} | Start: {request.start_date} | End: {request.end_date} | Periodicity: {request.periodicity} | Query ID: {query_id}')
        
        bloomberg_data = bloomberg.get_historical_data(
            request.security, 
            request.fields, 
            request.start_date, 
            request.end_date, 
            request.periodicity
        )
        
        if `"error`" in bloomberg_data:
            response = {
                'success': False,
                'data': None,
                'error': bloomberg_data['error'],
                'query_id': query_id
            }
        else:
            response = {
                'success': True,
                'data': {
                    'security': bloomberg_data['security'],
                    'fields': bloomberg_data['fields'],
                    'start_date': bloomberg_data['start_date'],
                    'end_date': bloomberg_data['end_date'],
                    'periodicity': bloomberg_data['periodicity'],
                    'data_points': len(bloomberg_data['data']),
                    'historical_data': bloomberg_data['data'],
                    'source': 'Bloomberg Terminal - HISTORICAL DATA'
                },
                'query_id': query_id
            }
        
        # Log successful response
        data_points = len(bloomberg_data.get('data', []))
        logger.info(f'Bloomberg historical response: {data_points} data points returned | Query ID: {query_id}')
        
        return response
        
    except Exception as e:
        # Log error
        logger.error(f'Bloomberg historical error: {str(e)} | Query ID: {query_id}')
        
        return {
            'success': False,
            'data': None,
            'error': str(e),
            'query_id': query_id
        }
"@

# Find the insertion point (before if __name__ == "__main__")
$insertionPoint = 'if __name__ == "__main__":'
$content = $content -replace $insertionPoint, ($historicalEndpoint + "`n" + $insertionPoint)

# Write the updated content
$content | Set-Content 'C:\BloombergAPI\main.py'

# Restart the API server
Write-Output "Stopping existing API server..."
Get-Process python* | Stop-Process -Force

Write-Output "Starting API server with historical endpoint..."
Start-Sleep -Seconds 3
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden

Write-Output "API server restarted with historical data endpoint"