# PROFESSIONAL BLOOMBERG API - ENHANCED VERSION
# ZERO TOLERANCE FOR MOCK DATA
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import uvicorn
import json

# Try to import Bloomberg API - handle gracefully if not available
try:
    import blpapi
    BLOOMBERG_AVAILABLE = True
    print("Bloomberg API (blpapi) imported successfully")
except ImportError:
    BLOOMBERG_AVAILABLE = False
    print("Bloomberg API (blpapi) not available - will return errors until installed")

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
    description="Production Bloomberg Terminal API - REAL DATA ONLY",
    version="1.0.0"
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

# API Key validation
VALID_API_KEYS = {"test": "bloomberg-client"}

def validate_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

# ==========================================
# BLOOMBERG CONNECTION - ENHANCED
# ==========================================

class BloombergSession:
    def __init__(self):
        self.session = None
        self.service = None
        self.is_connected = False
        
    def start(self):
        """Start Bloomberg session - Enhanced error handling"""
        if not BLOOMBERG_AVAILABLE:
            raise Exception("Bloomberg API (blpapi) not installed. Install Bloomberg Terminal and Python API package.")
        
        try:
            # Create session options
            session_options = blpapi.SessionOptions()
            session_options.setServerHost("localhost")
            session_options.setServerPort(8194)
            
            # Create session
            self.session = blpapi.Session(session_options)
            
            if not self.session.start():
                raise Exception("Failed to start Bloomberg session - Terminal not running or not logged in")
            
            # Open reference data service
            if not self.session.openService("//blp/refdata"):
                raise Exception("Failed to open Bloomberg reference data service - Terminal not authenticated")
            
            self.service = self.session.getService("//blp/refdata")
            self.is_connected = True
            
            logger.info("Bloomberg session started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Bloomberg connection failed: {e}")
            self.is_connected = False
            raise HTTPException(status_code=503, detail=f"Bloomberg Terminal not available: {e}")
    
    def get_reference_data(self, securities: List[str], fields: List[str]) -> Dict[str, Any]:
        """Get reference data from Bloomberg Terminal - NO CACHING"""
        if not self.is_connected:
            self.start()
        
        try:
            request = self.service.createRequest("ReferenceDataRequest")
            
            # Add securities
            for security in securities:
                request.append("securities", security)
            
            # Add fields
            for field in fields:
                request.append("fields", field)
            
            # Send request to Bloomberg Terminal
            self.session.sendRequest(request)
            
            # Process response - REAL DATA ONLY
            response_data = {}
            
            while True:
                event = self.session.nextEvent(5000)  # 5 second timeout
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    for msg in event:
                        response_data = self._process_response(msg)
                    break
                elif event.eventType() == blpapi.Event.TIMEOUT:
                    raise Exception("Bloomberg request timed out")
                elif event.eventType() == blpapi.Event.REQUEST_STATUS:
                    for msg in event:
                        logger.warning(f"Request status: {msg}")
            
            # VALIDATION: Reject any mock data indicators
            self._validate_real_data(response_data)
            
            return response_data
            
        except Exception as e:
            logger.error(f"Bloomberg data retrieval failed: {e}")
            raise HTTPException(status_code=500, detail=f"Bloomberg data retrieval failed: {e}")
    
    def _process_response(self, msg) -> Dict[str, Any]:
        """Process Bloomberg response - extract real data"""
        data = {}
        
        try:
            securities = msg.getElement("securityData")
            
            for i in range(securities.numValues()):
                security = securities.getValueAsElement(i)
                security_name = security.getElementAsString("security")
                
                # Check for security errors
                if security.hasElement("securityError"):
                    error_info = security.getElement("securityError")
                    error_msg = error_info.getElementAsString("message")
                    logger.warning(f"Security error for {security_name}: {error_msg}")
                    continue
                
                # Extract field data
                if security.hasElement("fieldData"):
                    field_data = security.getElement("fieldData")
                    security_data = {}
                    
                    for j in range(field_data.numElements()):
                        field = field_data.getElement(j)
                        field_name = field.name()
                        
                        if field.isNull():
                            security_data[field_name] = None
                        else:
                            # Handle different data types
                            if field.datatype() == blpapi.DataType.STRING:
                                security_data[field_name] = field.getValueAsString()
                            elif field.datatype() == blpapi.DataType.FLOAT64:
                                security_data[field_name] = field.getValueAsFloat()
                            elif field.datatype() == blpapi.DataType.INT32:
                                security_data[field_name] = field.getValueAsInt()
                            else:
                                security_data[field_name] = field.getValueAsString()
                    
                    data[security_name] = security_data
                    
        except Exception as e:
            logger.error(f"Error processing Bloomberg response: {e}")
            raise
        
        return data
    
    def _validate_real_data(self, data: Dict[str, Any]):
        """CRITICAL: Validate data is real, not mock"""
        data_str = json.dumps(data, default=str)
        
        # Check for mock data indicators
        mock_indicators = ["MOCK", "TEST", "DUMMY", "FAKE", "SIMULATED", "CACHED"]
        for indicator in mock_indicators:
            if indicator in data_str.upper():
                logger.error(f"MOCK DATA DETECTED: {indicator} found in response")
                raise HTTPException(status_code=500, detail="MOCK DATA REJECTED - Only real Bloomberg data allowed")
        
        # Validate reasonable data ranges for FX
        for security, fields in data.items():
            if isinstance(fields, dict):
                for field, value in fields.items():
                    if value is not None:
                        try:
                            float_val = float(value)
                            # Basic sanity checks for FX data
                            if field == "PX_LAST":
                                if float_val <= 0 or float_val > 1000:  # Reasonable FX range
                                    logger.warning(f"Suspicious FX rate: {security} {field} = {float_val}")
                            elif "VOL" in field:
                                if float_val < 0 or float_val > 500:  # Volatility percentage
                                    logger.warning(f"Suspicious volatility: {security} {field} = {float_val}")
                        except (ValueError, TypeError):
                            pass  # Non-numeric fields are OK
        
        logger.info(f"Real Bloomberg data validated: {len(data)} securities processed")

# Global Bloomberg session
bloomberg = BloombergSession()

# ==========================================
# PYDANTIC MODELS - ENHANCED
# ==========================================

class FXRatesRequest(BaseModel):
    currency_pairs: List[str]
    
    @validator('currency_pairs')
    def validate_currency_pairs(cls, v):
        # Comprehensive list of supported FX pairs
        valid_pairs = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
            'EURGBP', 'EURJPY', 'GBPJPY', 'EURCHF', 'AUDJPY', 'CADJPY', 'NZDJPY',
            'GBPCHF', 'AUDCHF', 'CADCHF', 'NZDCHF', 'EURAUD', 'GBPAUD', 'EURNZD',
            'GBPNZD', 'EURCAD', 'GBPCAD', 'AUDCAD', 'AUDNZD'
        ]
        for pair in v:
            if pair not in valid_pairs:
                raise ValueError(f"Unsupported currency pair: {pair}")
        return v

class FXVolatilityRequest(BaseModel):
    currency_pairs: List[str]
    tenors: List[str]
    
    @validator('currency_pairs')
    def validate_currency_pairs(cls, v):
        # Same validation as FXRatesRequest
        valid_pairs = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
            'EURGBP', 'EURJPY', 'GBPJPY', 'EURCHF', 'AUDJPY'
        ]
        for pair in v:
            if pair not in valid_pairs:
                raise ValueError(f"Unsupported currency pair: {pair}")
        return v
    
    @validator('tenors')
    def validate_tenors(cls, v):
        # Complete tenor list as per specification
        valid_tenors = ['O/N', 'T/N', '1W', '2W', '3W', '1M', '2M', '3M', '4M', '5M', '6M', '9M', '1Y', '18M', '2Y', '3Y', '5Y']
        for tenor in v:
            if tenor not in valid_tenors:
                raise ValueError(f"Unsupported tenor: {tenor}")
        return v

# ==========================================
# API ENDPOINTS - ENHANCED
# ==========================================

@app.get("/health")
async def health_check():
    """Enhanced health check with Bloomberg Terminal status"""
    bloomberg_connected = False
    bloomberg_error = None
    
    try:
        # Test Bloomberg connection
        if BLOOMBERG_AVAILABLE:
            bloomberg.start()
            bloomberg_connected = True
            logger.info("Health check: Bloomberg Terminal connected")
        else:
            bloomberg_error = "Bloomberg API (blpapi) not installed"
    except Exception as e:
        bloomberg_connected = False
        bloomberg_error = str(e)
        logger.warning(f"Health check: Bloomberg Terminal not available: {e}")
    
    return {
        "success": True,
        "data": {
            "api_status": "healthy",
            "bloomberg_api_available": BLOOMBERG_AVAILABLE,
            "bloomberg_terminal_running": bloomberg_connected,
            "bloomberg_service_available": bloomberg_connected,
            "bloomberg_error": bloomberg_error,
            "supported_fx_pairs": [
                "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
                "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "AUDJPY"
            ],
            "supported_tenors": ["O/N", "T/N", "1W", "2W", "3W", "1M", "2M", "3M", "4M", "5M", "6M", "9M", "1Y", "18M", "2Y", "3Y", "5Y"],
            "server_time": datetime.now().isoformat(),
            "is_using_mock_data": False
        },
        "error": bloomberg_error,
        "timestamp": datetime.now().isoformat(),
        "query_id": f"health_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    }

@app.post("/api/fx/rates/live")
async def get_live_fx_rates(request: FXRatesRequest, api_key: str = Depends(validate_api_key)):
    """Get live FX rates from Bloomberg Terminal - ENHANCED"""
    query_id = f"fx_rates_live_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    logger.info(f"FX rates request: {request.currency_pairs} | Query ID: {query_id}")
    
    try:
        # Build Bloomberg securities
        securities = [f"{pair} Curncy" for pair in request.currency_pairs]
        fields = ["PX_LAST", "PX_BID", "PX_ASK", "PX_OPEN", "PX_HIGH", "PX_LOW", "LAST_UPDATE_TIME"]
        
        # Get REAL data from Bloomberg Terminal
        bloomberg_data = bloomberg.get_reference_data(securities, fields)
        
        # Transform to API format
        rates = []
        for security, data in bloomberg_data.items():
            pair = security.replace(" Curncy", "")
            rates.append({
                "security": security,
                "currency_pair": pair,
                "PX_LAST": data.get("PX_LAST"),
                "PX_BID": data.get("PX_BID"),
                "PX_ASK": data.get("PX_ASK"),
                "PX_OPEN": data.get("PX_OPEN"),
                "PX_HIGH": data.get("PX_HIGH"),
                "PX_LOW": data.get("PX_LOW"),
                "LAST_UPDATE_TIME": data.get("LAST_UPDATE_TIME")
            })
        
        response = {
            "success": True,
            "data": {
                "data_type": "live_fx_rates",
                "timestamp": datetime.now().isoformat(),
                "currency_pairs": request.currency_pairs,
                "rate_types": ["SPOT", "BID", "ASK", "OPEN", "HIGH", "LOW"],
                "raw_data": rates,
                "source": "Bloomberg Terminal - LIVE DATA",
                "data_count": len(rates)
            },
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "query_id": query_id
        }
        
        logger.info(f"FX rates response: {len(rates)} rates returned | Query ID: {query_id}")
        return response
        
    except Exception as e:
        logger.error(f"FX rates error: {e} | Query ID: {query_id}")
        raise HTTPException(status_code=503, detail=f"Bloomberg Terminal not available: {e}")

@app.post("/api/fx/volatility/live")
async def get_live_fx_volatility(request: FXVolatilityRequest, api_key: str = Depends(validate_api_key)):
    """Get live FX volatility from Bloomberg Terminal - ENHANCED"""
    query_id = f"fx_vol_live_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    logger.info(f"FX volatility request: {request.currency_pairs} x {request.tenors} | Query ID: {query_id}")
    
    try:
        securities = []
        
        # Build comprehensive volatility securities
        for pair in request.currency_pairs:
            for tenor in request.tenors:
                # ATM Volatility
                securities.append(f"{pair}V{tenor} Curncy")
                
                # Risk Reversals (25 delta and 10 delta)
                securities.append(f"{pair}25RR{tenor} Curncy")
                securities.append(f"{pair}10RR{tenor} Curncy")
                
                # Butterflies (25 delta and 10 delta)
                securities.append(f"{pair}25BF{tenor} Curncy")
                securities.append(f"{pair}10BF{tenor} Curncy")
        
        # Bloomberg volatility fields
        fields = ["PX_LAST", "PX_BID", "PX_ASK", "LAST_UPDATE_TIME"]
        
        # Get REAL data from Bloomberg Terminal
        bloomberg_data = bloomberg.get_reference_data(securities, fields)
        
        # Transform to structured volatility surface
        volatility_data = []
        for security, data in bloomberg_data.items():
            volatility_data.append({
                "security": security,
                "PX_LAST": data.get("PX_LAST"),
                "PX_BID": data.get("PX_BID"),
                "PX_ASK": data.get("PX_ASK"),
                "LAST_UPDATE_TIME": data.get("LAST_UPDATE_TIME")
            })
        
        response = {
            "success": True,
            "data": {
                "data_type": "live_fx_volatility",
                "timestamp": datetime.now().isoformat(),
                "currency_pairs": request.currency_pairs,
                "tenors": request.tenors,
                "vol_types": ["ATM_VOL", "25D_RR", "25D_BF", "10D_RR", "10D_BF"],
                "raw_data": volatility_data,
                "source": "Bloomberg Terminal - LIVE DATA",
                "data_count": len(volatility_data)
            },
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "query_id": query_id
        }
        
        logger.info(f"FX volatility response: {len(volatility_data)} vol points returned | Query ID: {query_id}")
        return response
        
    except Exception as e:
        logger.error(f"FX volatility error: {e} | Query ID: {query_id}")
        raise HTTPException(status_code=503, detail=f"Bloomberg Terminal not available: {e}")

# ==========================================
# APPLICATION STARTUP
# ==========================================

if __name__ == "__main__":
    logger.info("Starting Enhanced Bloomberg FX Volatility API Server")
    logger.info("ZERO TOLERANCE FOR MOCK DATA - Will show no data until Bloomberg Terminal is connected")
    
    if not BLOOMBERG_AVAILABLE:
        logger.warning("Bloomberg API (blpapi) not available - install Bloomberg Terminal and Python API package")
    
    # Start server on all interfaces
    uvicorn.run(
        app,
        host="0.0.0.0",  # Bind to all network interfaces
        port=8080,
        log_level="info",
        access_log=True
    )