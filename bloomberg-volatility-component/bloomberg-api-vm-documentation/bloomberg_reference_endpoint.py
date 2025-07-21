# BLOOMBERG GENERIC REFERENCE DATA ENDPOINT
# To be added to C:\BloombergAPI\main.py on VM

# Add this import at the top
from typing import Optional

# Add these Pydantic models after the existing FXRatesRequest model

class BloombergReferenceRequest(BaseModel):
    """Generic Bloomberg reference data request"""
    securities: List[str]
    fields: List[str]
    overrides: Optional[Dict[str, str]] = None
    
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

# Add this endpoint after the existing /api/fx/rates/live endpoint

@app.post('/api/bloomberg/reference')
async def get_bloomberg_reference_data(
    request: BloombergReferenceRequest, 
    api_key: str = Depends(validate_api_key)
):
    """
    Generic Bloomberg reference data endpoint
    
    Examples:
    - FX Rates: securities=["EURUSD Curncy"], fields=["PX_LAST"]
    - Volatility: securities=["EURUSDV1M BGN Curncy"], fields=["PX_LAST"]
    - Bonds: securities=["GT10 Govt"], fields=["YLD_YTM_MID"]
    - Commodities: securities=["CL1 Comdty"], fields=["PX_LAST"]
    """
    query_id = f'reference_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    api_logger = comprehensive_logger.get_logger('api_requests')
    
    api_logger.info(f'Bloomberg reference request | Securities: {len(request.securities)} | Fields: {len(request.fields)} | Query ID: {query_id}')
    api_logger.info(f'Securities: {request.securities}')
    api_logger.info(f'Fields: {request.fields}')
    
    try:
        # Get data from Bloomberg
        comprehensive_logger.log_bloomberg_request(request.securities, request.fields, query_id)
        bloomberg_data = bloomberg.get_reference_data(request.securities, request.fields)
        
        # Build response with Bloomberg data exactly as returned
        securities_data = []
        errors = {}
        
        for security, data in bloomberg_data.items():
            if isinstance(data, dict):
                # Valid data returned
                securities_data.append({
                    'security': security,
                    'fields': data,
                    'success': True
                })
            else:
                # Error or no data
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
        
        # Return error response
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

# Note: The get_reference_data method in BloombergSession already exists and handles:
# - Creating Bloomberg request
# - Sending to Terminal
# - Processing response
# - Returning data dictionary