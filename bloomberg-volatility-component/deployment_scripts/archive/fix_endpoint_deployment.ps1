# PowerShell script to properly add Bloomberg reference endpoint

# 1. Backup current file
Copy-Item 'C:\BloombergAPI\main.py' 'C:\BloombergAPI\main_backup_fix.py'

# 2. Read the file content
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# 3. Find where to insert (before the if __name__ block)
$insertPoint = $content.IndexOf('if __name__ == "__main__":')

if ($insertPoint -eq -1) {
    Write-Error "Could not find main block"
    exit 1
}

# 4. Check if endpoint already exists in the wrong place
if ($content -match '@app\.post\(''/api/bloomberg/reference''\)') {
    # Remove the wrongly placed endpoint
    $pattern = '(?s)\n# Bloomberg Reference Request Model.*?query_id\s*\}'
    $content = $content -replace $pattern, ''
}

# 5. Create the endpoint code
$endpointCode = @'

# ==========================================
# BLOOMBERG GENERIC REFERENCE DATA ENDPOINT
# ==========================================

class BloombergReferenceRequest(BaseModel):
    """Generic Bloomberg reference data request"""
    securities: List[str]
    fields: List[str]
    
    @validator('securities')
    def validate_securities(cls, v):
        if not v:
            raise ValueError("At least one security required")
        if len(v) > 100:
            raise ValueError("Maximum 100 securities per request")
        return v
    
    @validator('fields')
    def validate_fields(cls, v):
        if not v:
            raise ValueError("At least one field required")
        if len(v) > 50:
            raise ValueError("Maximum 50 fields per request")
        return v

@app.post('/api/bloomberg/reference')
async def get_bloomberg_reference_data(
    request: BloombergReferenceRequest, 
    api_key: str = Depends(validate_api_key)
):
    """Generic Bloomberg reference data endpoint - REAL DATA ONLY"""
    query_id = f'reference_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    api_logger = comprehensive_logger.get_logger('api_requests')
    
    api_logger.info(f'Bloomberg reference request | Securities: {len(request.securities)} | Fields: {len(request.fields)} | Query ID: {query_id}')
    
    try:
        # Get data from Bloomberg
        comprehensive_logger.log_bloomberg_request(request.securities, request.fields, query_id)
        bloomberg_data = bloomberg.get_reference_data(request.securities, request.fields)
        
        # Build response
        securities_data = []
        errors = {}
        
        for security, data in bloomberg_data.items():
            if isinstance(data, dict):
                securities_data.append({
                    'security': security,
                    'fields': data,
                    'success': True
                })
            else:
                errors[security] = str(data)
                securities_data.append({
                    'security': security,
                    'fields': {},
                    'success': False,
                    'error': str(data)
                })
        
        response = {
            'success': True,
            'data': {
                'query_type': 'reference_data',
                'timestamp': datetime.now().isoformat(),
                'securities_requested': len(request.securities),
                'fields_requested': len(request.fields),
                'securities_returned': len(securities_data),
                'securities_data': securities_data,
                'errors': errors if errors else None,
                'source': 'Bloomberg Terminal - REFERENCE DATA'
            },
            'error': None,
            'timestamp': datetime.now().isoformat(),
            'query_id': query_id
        }
        
        api_logger.info(f'Bloomberg reference response: {len(securities_data)} securities processed | Query ID: {query_id}')
        return response
        
    except Exception as e:
        api_logger.error(f'Bloomberg reference error: {str(e)} | Query ID: {query_id}')
        comprehensive_logger.log_bloomberg_error(e, 'reference_data', query_id)
        
        return {
            'success': False,
            'data': None,
            'error': {
                'message': str(e),
                'type': type(e).__name__,
                'query_id': query_id
            },
            'timestamp': datetime.now().isoformat(),
            'query_id': query_id
        }

'@

# 6. Insert the endpoint code before the main block
$newContent = $content.Substring(0, $insertPoint) + $endpointCode + "`n`n" + $content.Substring($insertPoint)

# 7. Save the updated file
$newContent | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Endpoint added successfully"