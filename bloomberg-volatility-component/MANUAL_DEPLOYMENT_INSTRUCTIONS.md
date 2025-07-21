# MANUAL DEPLOYMENT INSTRUCTIONS

## OBJECTIVE
Add generic Bloomberg reference endpoint to VM API

## STEP 1: CONNECT TO VM
```
RDP or SSH to bloomberg-vm-02 (20.172.249.92)
Username: bloombergadmin
Password: [stored in environment]
```

## STEP 2: OPEN FILE
```
Navigate to: C:\BloombergAPI\main.py
Use Notepad++ or any text editor
```

## STEP 3: ADD CODE
Find line 342 (after the FX rates endpoint, before the logs endpoint)
Add this code:

```python

# Bloomberg Reference Request Model
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
    """Generic Bloomberg reference data endpoint"""
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
```

## STEP 4: SAVE FILE

## STEP 5: RESTART API
Open PowerShell as Administrator:
```powershell
# Stop current process
Get-Process python* | Stop-Process -Force

# Start new process
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList "main.py" -WindowStyle Hidden
```

## STEP 6: VERIFY
Test the endpoint:
```bash
curl http://20.172.249.92:8080/health
```

Then test reference endpoint with test script.