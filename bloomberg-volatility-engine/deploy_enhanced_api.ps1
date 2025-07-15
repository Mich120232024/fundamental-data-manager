# PowerShell script to deploy enhanced Bloomberg API to Azure VM
# This script should be run via Azure CLI run-command

$scriptContent = @'
# Stop existing API server
Get-Process python* | Stop-Process -Force -ErrorAction SilentlyContinue

# Create enhanced API script
$enhancedAPI = @"
#!/usr/bin/env python3
"""
Enhanced Bloomberg Terminal API Server
Adds support for FX Option Volatility Surface data (OVDV screen)
"""

import blpapi
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:*", "http://127.0.0.1:*", "http://10.225.1.27:*", "http://31.217.174.203:*"])

class BloombergTerminalAPI:
    def __init__(self):
        self.session = None
        self.service = None
        self.connected = False
        self.connect()
    
    def connect(self):
        """Connect to Bloomberg Terminal"""
        try:
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost("localhost")
            sessionOptions.setServerPort(8194)
            
            self.session = blpapi.Session(sessionOptions)
            
            if not self.session.start():
                logger.error("Failed to start Bloomberg session")
                return False
            
            if not self.session.openService("//blp/refdata"):
                logger.error("Failed to open Bloomberg service")
                return False
            
            self.service = self.session.getService("//blp/refdata")
            self.connected = True
            logger.info("Successfully connected to Bloomberg Terminal")
            return True
            
        except Exception as e:
            logger.error(f"Bloomberg connection error: {e}")
            self.connected = False
            return False
    
    def get_reference_data(self, securities, fields):
        """Get reference data from Bloomberg"""
        if not self.connected:
            return []
        
        try:
            request = self.service.createRequest("ReferenceDataRequest")
            
            # Add securities
            for security in securities:
                request.getElement("securities").appendValue(security)
            
            # Add fields
            for field in fields:
                request.getElement("fields").appendValue(field)
            
            self.session.sendRequest(request)
            
            results = []
            
            while True:
                event = self.session.nextEvent()
                
                for msg in event:
                    if msg.hasElement("responseError"):
                        logger.error(f"Response error: {msg.getElement('responseError')}")
                        continue
                    
                    if msg.hasElement("securityData"):
                        secDataArray = msg.getElement("securityData")
                        
                        for i in range(secDataArray.numValues()):
                            secData = secDataArray.getValueAsElement(i)
                            security = secData.getElementAsString("security")
                            
                            fieldData = {}
                            if secData.hasElement("fieldData"):
                                fields = secData.getElement("fieldData")
                                
                                for j in range(fields.numElements()):
                                    field = fields.getElement(j)
                                    fieldName = str(field.name())
                                    
                                    try:
                                        if field.isNull():
                                            fieldData[fieldName] = None
                                        elif field.datatype() == blpapi.DataType.FLOAT:
                                            fieldData[fieldName] = field.getValueAsFloat()
                                        elif field.datatype() == blpapi.DataType.INT:
                                            fieldData[fieldName] = field.getValueAsInteger()
                                        else:
                                            fieldData[fieldName] = str(field.getValue())
                                    except:
                                        fieldData[fieldName] = None
                            
                            results.append({
                                "security": security,
                                "fields": fieldData,
                                "timestamp": datetime.now().isoformat(),
                                "source": "Bloomberg Terminal"
                            })
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting reference data: {e}")
            return []

# Initialize Bloomberg connection
bloomberg = BloombergTerminalAPI()

# Keep existing endpoints
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "Enhanced Bloomberg Terminal API Server",
        "version": "4.0",
        "bloomberg_connected": bloomberg.connected,
        "bloomberg_available": bloomberg.connected,
        "mode": "REAL_TERMINAL_ENHANCED"
    })

@app.route('/api/market-data', methods=['POST'])
def get_market_data():
    """Enhanced market data endpoint"""
    data = request.json
    securities = data.get('securities', [])
    fields = data.get('fields', [])
    
    # Special handling for volatility surface fields
    if any("RR" in f or "BF" in f for f in fields):
        # Try alternative field names for FX options
        enhanced_fields = fields.copy()
        
        # Add Terminal-specific vol surface fields
        vol_surface_fields = [
            "VOLATILITY_90D",  # We know this works
            "OPT_DELTA_NEUTRAL_MID_VOL",
            "OPT_25D_CALL_IMP_VOL",
            "OPT_25D_PUT_IMP_VOL",
            "OPT_10D_CALL_IMP_VOL", 
            "OPT_10D_PUT_IMP_VOL"
        ]
        
        for vsf in vol_surface_fields:
            if vsf not in enhanced_fields:
                enhanced_fields.append(vsf)
        
        results = bloomberg.get_reference_data(securities, enhanced_fields)
        
        # Process results to calculate RR/BF if possible
        for result in results:
            fields_data = result.get("fields", {})
            
            # Try to calculate 25D RR from call/put vols
            call_25d = fields_data.get("OPT_25D_CALL_IMP_VOL")
            put_25d = fields_data.get("OPT_25D_PUT_IMP_VOL")
            
            if call_25d is not None and put_25d is not None:
                # Calculate risk reversal
                rr_25d = call_25d - put_25d
                
                # Add to results
                if "25D_RR_1M" in fields:
                    fields_data["25D_RR_1M"] = rr_25d
                
                # Calculate butterfly if ATM available
                atm_vol = fields_data.get("VOLATILITY_90D")
                if atm_vol is not None:
                    bf_25d = 0.5 * (call_25d + put_25d) - atm_vol
                    if "25D_BF_1M" in fields:
                        fields_data["25D_BF_1M"] = bf_25d
        
        return jsonify(results)
    
    # Standard market data request
    results = bloomberg.get_reference_data(securities, fields)
    return jsonify(results)

@app.route('/api/fx/rates')
def get_fx_rates():
    """Get FX rates"""
    pairs = request.args.getlist('pairs') or ["EURUSD", "GBPUSD", "USDJPY"]
    securities = [f"{pair} Curncy" for pair in pairs]
    fields = ["PX_LAST", "PX_BID", "PX_ASK", "CHG_PCT_1D"]
    
    results = bloomberg.get_reference_data(securities, fields)
    return jsonify(results)

if __name__ == '__main__':
    if bloomberg.connected:
        logger.info("Starting Enhanced Bloomberg API Server on port 8080")
        app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        logger.error("Failed to connect to Bloomberg Terminal")
        sys.exit(1)
"@

# Save enhanced API
$enhancedAPI | Out-File -FilePath "C:\Bloomberg\APIServer\enhanced_bloomberg_api.py" -Encoding UTF8

# Start the enhanced API server
cd C:\Bloomberg\APIServer
Start-Process C:\Python311\python.exe -ArgumentList 'enhanced_bloomberg_api.py' -WindowStyle Hidden

Write-Host "Enhanced Bloomberg API deployed and started"
'@

# Create the deployment command
$deployCommand = @"
az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 `
  --command-id RunPowerShellScript `
  --scripts "$scriptContent"
"@

# Save the command
Set-Content -Path "deploy_command.txt" -Value $deployCommand

Write-Host "Deployment script created. Run the command in deploy_command.txt to update the API server."