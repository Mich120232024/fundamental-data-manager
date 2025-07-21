# Safe deployment of historical data functionality
# This script carefully adds the historical method and endpoint

Write-Output "Starting safe historical data deployment..."

# First, backup current working version
Copy-Item 'C:\BloombergAPI\main.py' 'C:\BloombergAPI\main_before_historical.py'
Write-Output "Backed up current version"

# Read current content
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Add the historical data method to BloombergSession class
# Find the line "bloomberg = BloombergSession()" and insert method before it
$historicalMethod = @'

    def get_historical_data(self, security: str, fields: List[str], start_date: str, end_date: str, periodicity: str = "DAILY") -> Dict[str, Any]:
        """Get historical data from Bloomberg Terminal"""
        import blpapi
        
        if not self.session or not self.service:
            self.start()
            
        try:
            # Create historical data request
            request = self.service.createRequest("HistoricalDataRequest")
            
            # Add security
            request.getElement("securities").appendValue(security)
            
            # Add fields
            for field in fields:
                request.getElement("fields").appendValue(field)
                
            # Set date range
            request.set("startDate", start_date)
            request.set("endDate", end_date)
            request.set("periodicitySelection", periodicity)
            
            # Send request
            self.session.sendRequest(request)
            
            # Process response
            historical_data = []
            
            while True:
                event = self.session.nextEvent(5000)
                
                for msg in event:
                    if msg.messageType() == "HistoricalDataResponse":
                        securityData = msg.getElement("securityData")
                        security_name = securityData.getElement("security").getValueAsString()
                        
                        if securityData.hasElement("fieldData"):
                            fieldDataArray = securityData.getElement("fieldData")
                            
                            for i in range(fieldDataArray.numValues()):
                                fieldData = fieldDataArray.getValueAsElement(i)
                                date_str = fieldData.getElement("date").getValueAsString()
                                
                                data_point = {"date": date_str}
                                
                                for field in fields:
                                    if fieldData.hasElement(field):
                                        value = fieldData.getElement(field).getValue()
                                        data_point[field] = float(value) if isinstance(value, (int, float)) else str(value)
                                        
                                historical_data.append(data_point)
                                
                        if securityData.hasElement("securityError"):
                            error = securityData.getElement("securityError")
                            error_msg = error.getElement("message").getValueAsString()
                            return {
                                "error": f"Security error: {error_msg}",
                                "security": security
                            }
                            
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
                    
            return {
                "security": security,
                "fields": fields,
                "start_date": start_date,
                "end_date": end_date,
                "periodicity": periodicity,
                "data_points": len(historical_data),
                "data": historical_data
            }
            
        except Exception as e:
            logger.error(f"Historical data error: {e}")
            return {
                "error": f"Historical data error: {str(e)}",
                "security": security
            }
'@

# Insert the method before bloomberg = BloombergSession()
$content = $content -replace '(# Initialize Bloomberg connection\r?\nbloomberg = BloombergSession\(\))', ($historicalMethod + "`n`n" + '$1')

# Add the historical request model and endpoint
# Find the reference endpoint and add after it
$historicalEndpoint = @'


# Historical Bloomberg Data Request Model
class BloombergHistoricalRequest(BaseModel):
    security: str
    fields: List[str]
    start_date: str  # YYYYMMDD format
    end_date: str    # YYYYMMDD format
    periodicity: str = "DAILY"  # DAILY, WEEKLY, MONTHLY
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y%m%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYYMMDD format')
    
    @validator('periodicity')
    def validate_periodicity(cls, v):
        if v not in ["DAILY", "WEEKLY", "MONTHLY"]:
            raise ValueError('Periodicity must be DAILY, WEEKLY, or MONTHLY')
        return v

@app.post('/api/bloomberg/historical')
async def get_bloomberg_historical_data(
    request: BloombergHistoricalRequest, 
    api_key: str = Depends(validate_api_key)
):
    """Get historical data from Bloomberg Terminal"""
    query_id = f'historical_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    
    # Log the request
    logger.info(f'Bloomberg historical request | Security: {request.security} | Fields: {len(request.fields)} | Date range: {request.start_date} to {request.end_date} | Query ID: {query_id}')
    
    try:
        # Log detailed request
        logger.info(f'Bloomberg historical details - Security: {request.security} | Fields: {request.fields} | Start: {request.start_date} | End: {request.end_date} | Periodicity: {request.periodicity} | Query ID: {query_id}')
        
        # Get historical data
        bloomberg_data = bloomberg.get_historical_data(
            request.security, 
            request.fields, 
            request.start_date, 
            request.end_date, 
            request.periodicity
        )
        
        # Check for errors in response
        if "error" in bloomberg_data:
            logger.error(f'Bloomberg historical error: {bloomberg_data["error"]} | Query ID: {query_id}')
            return {
                'success': False,
                'data': None,
                'error': bloomberg_data['error'],
                'query_id': query_id
            }
        else:
            # Log successful response
            data_points = bloomberg_data.get('data_points', 0)
            logger.info(f'Bloomberg historical response: {data_points} data points returned | Query ID: {query_id}')
            
            return {
                'success': True,
                'data': bloomberg_data,
                'query_id': query_id
            }
        
    except Exception as e:
        # Log error
        logger.error(f'Bloomberg historical error: {str(e)} | Query ID: {query_id}')
        
        return {
            'success': False,
            'data': None,
            'error': str(e),
            'query_id': query_id
        }
'@

# Find the end of the reference endpoint and add historical after it
$insertPoint = "if __name__ == `"__main__`":"
$content = $content -replace $insertPoint, ($historicalEndpoint + "`n`n" + $insertPoint)

# Write the updated content
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Added historical data functionality"
Write-Output "- get_historical_data method added to BloombergSession"
Write-Output "- /api/bloomberg/historical endpoint added"
Write-Output "- Full logging implemented"

# Restart the API server
Write-Output "Stopping existing API server..."
Get-Process python* | Stop-Process -Force

Write-Output "Starting API server with historical support..."
Start-Sleep -Seconds 3
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden

Write-Output "API server restarted with historical data support"
Write-Output "Test with: POST /api/bloomberg/historical"