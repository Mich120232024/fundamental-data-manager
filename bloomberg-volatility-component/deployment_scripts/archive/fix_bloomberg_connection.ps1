# Fix Bloomberg connection in main.py

$code = @'
class BloombergSession:
    def __init__(self):
        self.session = None
        self.service = None
        
    def start(self):
        """Start Bloomberg session - connects to localhost:8194"""
        try:
            import blpapi
            # Bloomberg Terminal API settings
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost('localhost')
            sessionOptions.setServerPort(8194)
            
            # Create and start session
            self.session = blpapi.Session(sessionOptions)
            if not self.session.start():
                raise Exception("Failed to start Bloomberg session")
                
            # Open reference data service
            if not self.session.openService("//blp/refdata"):
                raise Exception("Failed to open Bloomberg reference data service")
                
            self.service = self.session.getService("//blp/refdata")
            logger.info("Bloomberg Terminal connected successfully")
            
        except Exception as e:
            logger.error(f"Bloomberg connection failed: {e}")
            raise Exception(f"Bloomberg Terminal not available: {e}")
    
    def get_reference_data(self, securities: List[str], fields: List[str]) -> Dict[str, Any]:
        """Get reference data from Bloomberg Terminal"""
        if not self.session or not self.service:
            self.start()
            
        results = {}
        
        try:
            import blpapi
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

# Backup current file
Copy-Item 'C:\BloombergAPI\main.py' 'C:\BloombergAPI\main_backup_before_bbg_fix.py'

# Read current file
$content = Get-Content 'C:\BloombergAPI\main.py' -Raw

# Find and replace the BloombergSession class
$pattern = '(?s)class BloombergSession:.*?(?=# Global Bloomberg session)'
$content = $content -replace $pattern, $code + "`n`n"

# Save updated file
$content | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Bloomberg connection fixed"