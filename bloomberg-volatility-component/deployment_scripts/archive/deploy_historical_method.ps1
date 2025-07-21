# Read the current main.py
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# The historical data method
$historicalMethod = @"

    def get_historical_data(self, security: str, fields: List[str], start_date: str, end_date: str, periodicity: str = "DAILY") -> Dict[str, Any]:
        `"``"``"Get historical data from Bloomberg Terminal`"``"``"
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
                event = self.session.nextEvent(500)
                
                for msg in event:
                    if msg.messageType() == "HistoricalDataResponse":
                        securityData = msg.getElement("securityData")
                        security_name = securityData.getElement("security").getValueAsString()
                        
                        if securityData.hasElement("fieldData"):
                            fieldDataArray = securityData.getElement("fieldData")
                            
                            for i in range(fieldDataArray.numValues()):
                                fieldData = fieldDataArray.getValueAsElement(i)
                                date_str = fieldData.getElement("date").getValueAsString()
                                
                                data_point = {`"date`": date_str}
                                
                                for field in fields:
                                    if fieldData.hasElement(field):
                                        value = fieldData.getElement(field).getValue()
                                        data_point[field] = float(value) if isinstance(value, (int, float)) else str(value)
                                        
                                historical_data.append(data_point)
                                
                        if securityData.hasElement("securityError"):
                            error = securityData.getElement("securityError")
                            return {`"error`": error.getElement(`"message`").getValueAsString()}
                            
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
                    
            return {
                `"security`": security,
                `"fields`": fields,
                `"start_date`": start_date,
                `"end_date`": end_date,
                `"periodicity`": periodicity,
                `"data`": historical_data
            }
            
        except Exception as e:
            logger.error(f`"Historical data error: {e}`")
            return {`"error`": str(e)}
"@

# Add the historical method before the bloomberg instance creation
$insertionPoint = "bloomberg = BloombergSession()"
$content = $content -replace $insertionPoint, ($historicalMethod + "`n`n" + $insertionPoint)

# Write the updated content
$content | Set-Content 'C:\BloombergAPI\main.py'

Write-Output "Added historical data method to BloombergSession class"