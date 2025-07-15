#!/usr/bin/env python3
"""
Enhanced Bloomberg Terminal API Server
Adds support for FX Option Volatility Surface data (OVDV screen)
"""

import blpapi
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import sys

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
    
    def get_fx_option_volatilities(self, currency_pair, tenors=None):
        """
        Get FX option volatility surface data including RR and BF
        Uses Terminal OVDV screen data
        """
        if not self.connected:
            return {"error": "Bloomberg not connected"}
        
        if tenors is None:
            tenors = ["1M", "3M", "6M", "1Y"]
        
        try:
            request = self.service.createRequest("ReferenceDataRequest")
            
            # Base currency pair
            base_ticker = f"{currency_pair} Curncy"
            
            # Build comprehensive field list for volatility surface
            fields = []
            
            # ATM Volatilities
            for tenor in tenors:
                fields.append(f"VOLATILITY_{tenor}")
                fields.append(f"FX_VOLATILITY_ATM_{tenor}")
            
            # Risk Reversals
            for tenor in tenors:
                fields.append(f"RISK_REVERSAL_25D_{tenor}")
                fields.append(f"FX_25D_RR_{tenor}")
                fields.append(f"25_DELTA_RISK_REVERSAL_{tenor}")
            
            # Butterflies
            for tenor in tenors:
                fields.append(f"BUTTERFLY_25D_{tenor}")
                fields.append(f"FX_25D_BF_{tenor}")
                fields.append(f"25_DELTA_BUTTERFLY_{tenor}")
            
            # Individual strike vols
            for tenor in tenors:
                fields.extend([
                    f"FX_VOLATILITY_25D_CALL_{tenor}",
                    f"FX_VOLATILITY_25D_PUT_{tenor}",
                    f"FX_VOLATILITY_10D_CALL_{tenor}",
                    f"FX_VOLATILITY_10D_PUT_{tenor}"
                ])
            
            # Add security and fields to request
            request.getElement("securities").appendValue(base_ticker)
            fieldElement = request.getElement("fields")
            for field in fields:
                fieldElement.appendValue(field)
            
            # Send request
            self.session.sendRequest(request)
            
            # Process response
            result = {
                "pair": currency_pair,
                "timestamp": datetime.now().isoformat(),
                "atmVols": {},
                "riskReversals": {"25D": {}},
                "butterflies": {"25D": {}},
                "strikes": {"25D_Call": {}, "25D_Put": {}}
            }
            
            while True:
                event = self.session.nextEvent()
                
                for msg in event:
                    if msg.hasElement("responseError"):
                        logger.error(f"Response error: {msg.getElement('responseError')}")
                        continue
                    
                    if msg.hasElement("securityData"):
                        securityData = msg.getElement("securityData")
                        fieldData = securityData.getElement("fieldData")
                        
                        # Parse response fields
                        for tenor in tenors:
                            # ATM vols
                            for atm_field in [f"VOLATILITY_{tenor}", f"FX_VOLATILITY_ATM_{tenor}"]:
                                if fieldData.hasElement(atm_field):
                                    result["atmVols"][tenor] = fieldData.getElementAsFloat(atm_field)
                                    break
                            
                            # Risk Reversals
                            for rr_field in [f"RISK_REVERSAL_25D_{tenor}", f"FX_25D_RR_{tenor}", f"25_DELTA_RISK_REVERSAL_{tenor}"]:
                                if fieldData.hasElement(rr_field):
                                    result["riskReversals"]["25D"][tenor] = fieldData.getElementAsFloat(rr_field)
                                    break
                            
                            # Butterflies
                            for bf_field in [f"BUTTERFLY_25D_{tenor}", f"FX_25D_BF_{tenor}", f"25_DELTA_BUTTERFLY_{tenor}"]:
                                if fieldData.hasElement(bf_field):
                                    result["butterflies"]["25D"][tenor] = fieldData.getElementAsFloat(bf_field)
                                    break
                            
                            # Individual strikes
                            call_field = f"FX_VOLATILITY_25D_CALL_{tenor}"
                            put_field = f"FX_VOLATILITY_25D_PUT_{tenor}"
                            
                            if fieldData.hasElement(call_field):
                                result["strikes"]["25D_Call"][tenor] = fieldData.getElementAsFloat(call_field)
                            if fieldData.hasElement(put_field):
                                result["strikes"]["25D_Put"][tenor] = fieldData.getElementAsFloat(put_field)
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            
            # If no direct RR/BF, calculate from strikes
            for tenor in tenors:
                if tenor not in result["riskReversals"]["25D"] and \
                   tenor in result["strikes"]["25D_Call"] and \
                   tenor in result["strikes"]["25D_Put"]:
                    call_vol = result["strikes"]["25D_Call"][tenor]
                    put_vol = result["strikes"]["25D_Put"][tenor]
                    result["riskReversals"]["25D"][tenor] = call_vol - put_vol
                
                if tenor not in result["butterflies"]["25D"] and \
                   tenor in result["strikes"]["25D_Call"] and \
                   tenor in result["strikes"]["25D_Put"] and \
                   tenor in result["atmVols"]:
                    call_vol = result["strikes"]["25D_Call"][tenor]
                    put_vol = result["strikes"]["25D_Put"][tenor]
                    atm_vol = result["atmVols"][tenor]
                    result["butterflies"]["25D"][tenor] = 0.5 * (call_vol + put_vol) - atm_vol
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting FX option volatilities: {e}")
            return {"error": str(e)}
    
    def get_ovdv_surface(self, currency_pair):
        """
        Alternative approach: Get OVDV screen data directly
        """
        if not self.connected:
            return {"error": "Bloomberg not connected"}
        
        try:
            # Use BDS (Bulk Data Service) for OVDV screen
            request = self.service.createRequest("ReferenceDataRequest")
            
            ticker = f"{currency_pair} Curncy"
            request.getElement("securities").appendValue(ticker)
            
            # Request OVDV surface data
            request.getElement("fields").appendValue("OVDV_SURFACE")
            
            # Add overrides for specific surface
            overrides = request.getElement("overrides")
            override1 = overrides.appendElement()
            override1.setElement("fieldId", "OVDV_SURFACE_TYPE")
            override1.setElement("value", "IMPLIED_VOLATILITY")
            
            self.session.sendRequest(request)
            
            surface_data = {
                "pair": currency_pair,
                "timestamp": datetime.now().isoformat(),
                "surface": []
            }
            
            while True:
                event = self.session.nextEvent()
                
                for msg in event:
                    if msg.hasElement("responseError"):
                        logger.error(f"OVDV error: {msg.getElement('responseError')}")
                        continue
                    
                    if msg.hasElement("securityData"):
                        securityData = msg.getElement("securityData")
                        if securityData.hasElement("fieldData"):
                            fieldData = securityData.getElement("fieldData")
                            
                            if fieldData.hasElement("OVDV_SURFACE"):
                                surface = fieldData.getElement("OVDV_SURFACE")
                                
                                # Parse surface data
                                for i in range(surface.numValues()):
                                    point = surface.getValueAsElement(i)
                                    surface_data["surface"].append({
                                        "tenor": point.getElementAsString("TENOR") if point.hasElement("TENOR") else None,
                                        "delta": point.getElementAsFloat("DELTA") if point.hasElement("DELTA") else None,
                                        "volatility": point.getElementAsFloat("VOLATILITY") if point.hasElement("VOLATILITY") else None
                                    })
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            
            return surface_data
            
        except Exception as e:
            logger.error(f"Error getting OVDV surface: {e}")
            return {"error": str(e)}

# Initialize Bloomberg connection
bloomberg = BloombergTerminalAPI()

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "Enhanced Bloomberg Terminal API Server",
        "version": "4.0",
        "bloomberg_connected": bloomberg.connected,
        "bloomberg_available": bloomberg.connected,
        "mode": "REAL_TERMINAL_ENHANCED"
    })

@app.route('/api/fx/volatility-surface/<pair>')
def get_volatility_surface(pair):
    """Get complete FX option volatility surface"""
    tenors = request.args.getlist('tenors') or ["1M", "3M", "6M", "1Y"]
    
    result = bloomberg.get_fx_option_volatilities(pair.upper(), tenors)
    
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify(result)

@app.route('/api/fx/ovdv/<pair>')
def get_ovdv_surface(pair):
    """Get OVDV screen surface data"""
    result = bloomberg.get_ovdv_surface(pair.upper())
    
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify(result)

@app.route('/api/market-data', methods=['POST'])
def get_market_data():
    """Enhanced market data endpoint with volatility surface support"""
    data = request.json
    securities = data.get('securities', [])
    fields = data.get('fields', [])
    
    # Check if requesting volatility surface fields
    vol_surface_fields = [
        "25D_RR_1M", "25D_RR_3M", "25D_RR_6M", "25D_RR_1Y",
        "25D_BF_1M", "25D_BF_3M", "25D_BF_6M", "25D_BF_1Y"
    ]
    
    requesting_vol_surface = any(field in vol_surface_fields for field in fields)
    
    if requesting_vol_surface and len(securities) == 1 and "Curncy" in securities[0]:
        # Extract currency pair
        pair = securities[0].replace(" Curncy", "")
        
        # Get volatility surface data
        vol_data = bloomberg.get_fx_option_volatilities(pair, ["1M", "3M", "6M", "1Y"])
        
        # Format response to match expected structure
        response_fields = {}
        
        # Map requested fields to data
        for field in fields:
            if "RR" in field:
                # Risk Reversal
                tenor = field.split("_")[-1]  # Extract tenor (1M, 3M, etc.)
                if tenor in vol_data["riskReversals"]["25D"]:
                    response_fields[field] = vol_data["riskReversals"]["25D"][tenor]
                else:
                    response_fields[field] = None
            elif "BF" in field:
                # Butterfly
                tenor = field.split("_")[-1]
                if tenor in vol_data["butterflies"]["25D"]:
                    response_fields[field] = vol_data["butterflies"]["25D"][tenor]
                else:
                    response_fields[field] = None
            else:
                response_fields[field] = None
        
        return jsonify([{
            "security": securities[0],
            "fields": response_fields,
            "timestamp": datetime.now().isoformat(),
            "source": "Bloomberg Terminal OVDV"
        }])
    
    # Fall back to standard market data handling
    # (Include existing market data logic here)
    return jsonify([{
        "security": sec,
        "fields": {field: None for field in fields},
        "timestamp": datetime.now().isoformat(),
        "source": "Bloomberg Terminal"
    } for sec in securities])

if __name__ == '__main__':
    if bloomberg.connected:
        logger.info("Starting Enhanced Bloomberg API Server on port 8080")
        app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        logger.error("Failed to connect to Bloomberg Terminal")
        sys.exit(1)