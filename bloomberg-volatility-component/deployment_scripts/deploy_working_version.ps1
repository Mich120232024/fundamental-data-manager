# Deploy the exact working version of main.py
# This preserves all our good work: health check, FX rates, generic reference endpoint, logging

$workingContent = @'
# PROFESSIONAL BLOOMBERG API - ZERO TOLERANCE FOR MOCK DATA
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import uvicorn
import json
import os

# ==========================================
# CRITICAL: ZERO TOLERANCE FOR MOCK DATA
# ==========================================

# Configure logging - AUDIT ALL REQUESTS
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/BloombergAPI/logs/api_requests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(
    title="Bloomberg FX Volatility API",
    description="PROFESSIONAL GRADE - ZERO TOLERANCE FOR MOCK DATA",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def validate_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "test":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

# ==========================================
# BLOOMBERG TERMINAL CONNECTION
# ==========================================

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
            
        except ImportError:
            raise Exception("Bloomberg API not available - blpapi package not installed")
        except Exception as e:
            logger.error(f"Bloomberg connection failed: {e}")
            raise Exception(f"Bloomberg Terminal not available: {e}")
    
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
                            security = securityData.getElement("security").getValueAsString()
                            
                            if securityData.hasElement("fieldData"):
                                fieldData = securityData.getElement("fieldData")
                                data = {}
                                
                                for j in range(fieldData.numElements()):
                                    field = fieldData.getElement(j)
                                    field_name = str(field.name())
                                    field_value = field.getValue()
                                    data[field_name] = field_value
                                    
                                results[security] = data
                                
                            if securityData.hasElement("securityError"):
                                error = securityData.getElement("securityError")
                                results[security] = f"Error: {error.getElement('message').getValueAsString()}"
                                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
                    
        except Exception as e:
            logger.error(f"Bloomberg data request failed: {e}")
            raise Exception(f"Bloomberg data request failed: {e}")
            
        return results

# Initialize Bloomberg connection
bloomberg = BloombergSession()

# ==========================================
# REQUEST MODELS
# ==========================================

class FXRatesRequest(BaseModel):
    currency_pairs: List[str]

class FXVolatilityRequest(BaseModel):
    currency_pairs: List[str]
    tenors: List[str]

# Generic Bloomberg Reference Data Endpoint
class BloombergReferenceRequest(BaseModel):
    securities: List[str]
    fields: List[str]

# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/health")
async def health_check():
    """Comprehensive health check with Bloomberg Terminal validation"""
    query_id = f'health_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    
    try:
        # Test Bloomberg connection
        bloomberg.start()
        bloomberg_available = True
        bloomberg_error = None
        logger.info("Bloomberg Terminal connected successfully")
        logger.info("Health check: Bloomberg Terminal connected")
        
    except Exception as e:
        bloomberg_available = False
        bloomberg_error = str(e)
        logger.warning(f"Health check: Bloomberg Terminal not available: {e}")
    
    return {
        "success": True,
        "data": {
            "api_status": "healthy",
            "bloomberg_terminal_running": bloomberg_available,
            "bloomberg_service_available": bloomberg_available,
            "supported_fx_pairs": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"],
            "supported_tenors": ["1W", "2W", "1M", "2M", "3M", "6M", "9M", "1Y", "2Y"],
            "server_time": datetime.now().isoformat(),
            "is_using_mock_data": False
        },
        "error": bloomberg_error,
        "timestamp": datetime.now().isoformat(),
        "query_id": query_id
    }

@app.post("/api/fx/rates/live")
async def get_fx_rates(request: FXRatesRequest, api_key: str = Depends(validate_api_key)):
    """Get live FX rates from Bloomberg Terminal - REAL DATA ONLY"""
    query_id = f'fx_rates_live_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    logger.info(f"FX rates request: {request.currency_pairs} | Query ID: {query_id}")
    
    try:
        # Build Bloomberg securities
        securities = [f"{pair} Curncy" for pair in request.currency_pairs]
        fields = ["PX_LAST", "PX_BID", "PX_ASK", "PX_OPEN", "PX_HIGH", "PX_LOW"]
        
        # Get REAL data from Bloomberg Terminal
        bloomberg_data = bloomberg.get_reference_data(securities, fields)
        
        # Process results
        fx_data = []
        for security, data in bloomberg_data.items():
            if isinstance(data, dict):
                pair = security.replace(" Curncy", "")
                fx_data.append({
                    "security": security,
                    "currency_pair": pair,
                    "PX_LAST": data.get("PX_LAST"),
                    "PX_BID": data.get("PX_BID"), 
                    "PX_ASK": data.get("PX_ASK"),
                    "PX_OPEN": data.get("PX_OPEN"),
                    "PX_HIGH": data.get("PX_HIGH"),
                    "PX_LOW": data.get("PX_LOW"),
                    "LAST_UPDATE_TIME": datetime.now().isoformat()
                })
        
        return {
            "success": True,
            "data": {
                "data_type": "live_fx_rates",
                "timestamp": datetime.now().isoformat(),
                "currency_pairs": request.currency_pairs,
                "rate_types": ["SPOT", "BID", "ASK", "OPEN", "HIGH", "LOW"],
                "raw_data": fx_data,
                "source": "Bloomberg Terminal - LIVE DATA",
                "data_count": len(fx_data)
            },
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "query_id": query_id
        }
        
    except Exception as e:
        logger.error(f"FX rates error: {e} | Query ID: {query_id}")
        raise HTTPException(status_code=503, detail=f"Bloomberg Terminal not available: {e}")

@app.post('/api/bloomberg/reference')
async def get_bloomberg_reference_data(request: BloombergReferenceRequest, api_key: str = Depends(validate_api_key)):
    query_id = f'reference_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    
    # Log the request
    logger.info(f'Bloomberg reference request | Securities: {len(request.securities)} | Fields: {len(request.fields)} | Query ID: {query_id}')
    
    try:
        # Log the Bloomberg request
        logger.info(f'Bloomberg request - Securities: {request.securities} | Fields: {request.fields} | Query ID: {query_id}')
        
        bloomberg_data = bloomberg.get_reference_data(request.securities, request.fields)
        
        securities_data = []
        for security, data in bloomberg_data.items():
            if isinstance(data, dict):
                securities_data.append({
                    'security': security,
                    'fields': data,
                    'success': True
                })
            else:
                securities_data.append({
                    'security': security,
                    'fields': {},
                    'success': False,
                    'error': str(data)
                })
        
        response = {
            'success': True,
            'data': {
                'securities_data': securities_data,
                'source': 'Bloomberg Terminal'
            }
        }
        
        # Log successful response
        logger.info(f'Bloomberg reference response: {len(securities_data)} securities processed | Query ID: {query_id}')
        
        return response
        
    except Exception as e:
        # Log error
        logger.error(f'Bloomberg reference error: {str(e)} | Query ID: {query_id}')
        
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    logger.info("Starting Bloomberg FX Volatility API Server - REAL DATA ONLY")
    logger.info("ZERO TOLERANCE FOR MOCK DATA - Will show no data until Bloomberg Terminal is connected")
    
    # Start server on all interfaces
    uvicorn.run(
        app,
        host="0.0.0.0",  # Bind to all network interfaces
        port=8080,
        log_level="info",
        access_log=True
    )
'@

# Write the working content to main.py
$workingContent | Set-Content 'C:\BloombergAPI\main.py' -Encoding UTF8

Write-Output "Deployed exact working version - preserving all good work"
Write-Output "Features restored:"
Write-Output "- Health endpoint"
Write-Output "- FX rates endpoint" 
Write-Output "- Generic reference endpoint with logging"
Write-Output "- Real Bloomberg Terminal connection"
Write-Output "- Zero tolerance for mock data"

# Start the API server
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden

Write-Output "API server started with all working features"