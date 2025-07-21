# Patch get_reference_data to actually fetch Bloomberg data

$getReferenceMethod = @'
    def get_reference_data(self, securities: List[str], fields: List[str]) -> Dict[str, Any]:
        """Get reference data from Bloomberg Terminal"""
        import blpapi
        
        if not self.session or not self.service:
            self.start()
            
        results = {}
        
        try:
            # Create request
            request = self.service.createRequest("ReferenceDataRequest")
            
            # Add securities
            for security in securities:
                request.getElement("securities").appendValue(security)
                
            # Add fields
            for field in fields:
                request.getElement("fields").appendValue(field)
                
            # Send request
            self.session.sendRequest(request)
            
            # Process response
            while True:
                event = self.session.nextEvent(500)
                
                for msg in event:
                    if msg.messageType() == "ReferenceDataResponse":
                        securityDataArray = msg.getElement("securityData")
                        
                        for i in range(securityDataArray.numValues()):
                            securityData = securityDataArray.getValueAsElement(i)
                            security = securityData.getElementAsString("security")
                            
                            if securityData.hasElement("securityError"):
                                error = securityData.getElement("securityError")
                                results[security] = f"Error: {error.getElementAsString('message')}"
                            else:
                                fieldData = securityData.getElement("fieldData")
                                data = {}
                                
                                for field in fields:
                                    if fieldData.hasElement(field):
                                        element = fieldData.getElement(field)
                                        # Handle different data types
                                        if element.datatype() == blpapi.DataType.FLOAT64:
                                            data[field] = element.getValueAsFloat()
                                        elif element.datatype() == blpapi.DataType.INT32:
                                            data[field] = element.getValueAsInteger()
                                        else:
                                            data[field] = element.getValueAsString()
                                    else:
                                        data[field] = None
                                        
                                results[security] = data
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
                    
            return results
            
        except Exception as e:
            logger.error(f"Bloomberg data request failed: {e}")
            raise HTTPException(status_code=503, detail="Bloomberg Terminal not available - NO MOCK DATA PROVIDED")
'@

# Read current file
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Replace the get_reference_data method
$pattern = '(?s)def get_reference_data\(self.*?(?=\n\n# Global Bloomberg session)'
$newContent = $content -replace $pattern, $getReferenceMethod.TrimStart()

# Save
$newContent | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Patched get_reference_data() method"