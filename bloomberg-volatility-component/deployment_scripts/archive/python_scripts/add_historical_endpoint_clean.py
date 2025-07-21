# Clean implementation of historical data functionality
# This adds the historical method and endpoint to our working API

# First, the historical data method for BloombergSession class
historical_method = '''
    def get_historical_data(self, security: str, fields: List[str], start_date: str, end_date: str, periodicity: str = "DAILY") -> Dict[str, Any]:
        """Get historical data from Bloomberg Terminal
        
        Args:
            security: Bloomberg security (e.g., "EURUSD10B1M BGN Curncy")
            fields: List of fields (e.g., ["PX_LAST", "PX_BID", "PX_ASK"])
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
            periodicity: DAILY, WEEKLY, or MONTHLY
            
        Returns:
            Dict with historical data or error
        """
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
                event = self.session.nextEvent(5000)  # 5 second timeout
                
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
'''

# Now the request model and endpoint
historical_endpoint = '''
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
    """Get historical data from Bloomberg Terminal
    
    Example: Get 10D butterfly for last 10 days
    POST /api/bloomberg/historical
    {
        "security": "EURUSD10B1M BGN Curncy",
        "fields": ["PX_LAST", "PX_BID", "PX_ASK"],
        "start_date": "20250706",
        "end_date": "20250716",
        "periodicity": "DAILY"
    }
    """
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
'''

print("Historical implementation created with full logging")
print("Features:")
print("- get_historical_data method for BloombergSession")
print("- BloombergHistoricalRequest model with validation")
print("- /api/bloomberg/historical endpoint")
print("- Complete request/response logging")
print("- Error handling for security errors")
print("- Support for DAILY, WEEKLY, MONTHLY periodicity")