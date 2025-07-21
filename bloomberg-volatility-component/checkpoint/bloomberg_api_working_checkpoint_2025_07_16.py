

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
,
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
          for i in range(securityDataArray.numValues()):
                        
                        securityDataArray = msg.getElement("securityData")
                    if msg.messageType() == "ReferenceDataResponse":
                for msg in event:
                
                event = self.session.nextEvent(500)
            while True:
            # Process response
            
            self.session.sendRequest(request)
            # Send request
                
                request.getElement("fields").appendValue(field)
            for field in fields:
            # Add fields
                
                request.getElement("securities").appendValue(security)
            for security in securities:
            # Add securities
            
            request = self.service.createRequest("ReferenceDataRequest")
            # Create request
        try:
        
        results = {}
            
            self.start()
        if not self.session or not self.service:
        
        import blpapi
        """Get reference data from Bloomberg Terminal"""
    def get_reference_data(self, securities: List[str], fields: List[str]) -> Dict[str, Any]:
    
            raise Exception(f"Bloomberg Terminal not available: {e}")
            logger.error(f"Bloomberg connection failed: {e}")
        except Exception as e:
            raise Exception("Bloomberg API not available - blpapi package not installed")
        except ImportError:
            
            logger.info("Bloomberg Terminal connected successfully")
            self.service = self.session.getService("//blp/refdata")
                
                raise Exception("Failed to open Bloomberg reference data service")
            if not self.session.openService("//blp/refdata"):
            # Open reference data service
                
                raise Exception("Failed to start Bloomberg session")
            if not self.session.start():
            self.session = blpapi.Session(sessionOptions)
            # Create and start session
            
            sessionOptions.setServerPort(8194)
            sessionOptions.setServerHost('localhost')
            sessionOptions = blpapi.SessionOptions()
            # Bloomberg Terminal API settings
            import blpapi
        try:
        """Start Bloomberg session - connects to localhost:8194"""
    def start(self):
        
        self.service = None
        self.session = None
    def __init__(self):
class BloombergSession:

# ==========================================
# BLOOMBERG TERMINAL CONNECTION
# ==========================================

    return credentials.credentials
        raise HTTPException(status_code=401, detail="Invalid API key")
    if credentials.credentials != "test":
def validate_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):

security = HTTPBearer()
# Security

)
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_origins=["*"],
    CORSMiddleware,
app.add_middleware(
# CORS configuration

)
    version="2.0.0"
    description="PROFESSIONAL GRADE - ZERO TOLERANCE FOR MOCK DATA",
    title="Bloomberg FX Volatility API",
app = FastAPI(
# FastAPI application

logger = logging.getLogger(__name__)

)
    ]
        logging.StreamHandler()
        logging.FileHandler('C:/BloombergAPI/logs/api_requests.log'),
    handlers=[
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
logging.basicConfig(
# Configure logging - AUDIT ALL REQUESTS

# ==========================================
# CRITICAL: ZERO TOLERANCE FOR MOCK DATA
# ==========================================

import os
import json
import uvicorn
from pydantic import BaseModel, validator
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, HTTPException, Depends, Security
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
# PROFESSIONAL BLOOMBERG API - ZERO TOLERANCE FOR MOCK DATA
    )
