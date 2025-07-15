#!/usr/bin/env python3
"""
Bloomberg Terminal API Server v5.0
Full flexibility for FX Option Volatility Surface extraction
"""

import blpapi
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import sys
import json
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for flexibility

class BloombergTerminalAPI:
    def __init__(self):
        self.session = None
        self.service = None
        self.connected = False
        self.cache = {}  # Cache for frequently requested data
        self.cache_timeout = 60  # Cache for 60 seconds
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
    
    def get_field_value(self, element):
        """Extract value from Bloomberg field element"""
        try:
            if element.isNull():
                return None
            
            dtype = element.datatype()
            
            if dtype == blpapi.DataType.FLOAT:
                return element.getValueAsFloat()
            elif dtype == blpapi.DataType.INT:
                return element.getValueAsInteger()
            elif dtype == blpapi.DataType.STRING:
                return element.getValueAsString()
            elif dtype == blpapi.DataType.DATE:
                return element.getValueAsString()
            elif dtype == blpapi.DataType.DATETIME:
                return element.getValueAsString()
            elif dtype == blpapi.DataType.BOOL:
                return element.getValueAsBool()
            else:
                return str(element.getValue())
        except:
            return None
    
    def get_reference_data(self, securities, fields, overrides=None):
        """Get reference data with optional overrides"""
        if not self.connected:
            return []
        
        try:
            request = self.service.createRequest("ReferenceDataRequest")
            
            # Add securities
            securities_element = request.getElement("securities")
            for security in securities:
                securities_element.appendValue(security)
            
            # Add fields
            fields_element = request.getElement("fields")
            for field in fields:
                fields_element.appendValue(field)
            
            # Add overrides if provided
            if overrides:
                overrides_element = request.getElement("overrides")
                for override_field, override_value in overrides.items():
                    override = overrides_element.appendElement()
                    override.setElement("fieldId", override_field)
                    override.setElement("value", override_value)
            
            self.session.sendRequest(request)
            
            results = []
            
            while True:
                event = self.session.nextEvent()
                
                for msg in event:
                    if msg.hasElement("responseError"):
                        error = msg.getElement("responseError")
                        logger.error(f"Response error: {error}")
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
                                    fieldData[fieldName] = self.get_field_value(field)
                            
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
    
    def get_bulk_data(self, security, field):
        """Get bulk data (for matrix/surface data)"""
        if not self.connected:
            return None
        
        try:
            request = self.service.createRequest("ReferenceDataRequest")
            request.getElement("securities").appendValue(security)
            request.getElement("fields").appendValue(field)
            
            self.session.sendRequest(request)
            
            while True:
                event = self.session.nextEvent()
                
                for msg in event:
                    if msg.hasElement("responseError"):
                        logger.error(f"Bulk data error: {msg.getElement('responseError')}")
                        continue
                    
                    if msg.hasElement("securityData"):
                        secData = msg.getElement("securityData").getValueAsElement(0)
                        
                        if secData.hasElement("fieldData"):
                            fieldData = secData.getElement("fieldData")
                            
                            if fieldData.hasElement(field):
                                bulkField = fieldData.getElement(field)
                                
                                # Parse bulk data
                                bulk_data = []
                                for i in range(bulkField.numValues()):
                                    row = bulkField.getValueAsElement(i)
                                    row_data = {}
                                    
                                    for j in range(row.numElements()):
                                        elem = row.getElement(j)
                                        row_data[str(elem.name())] = self.get_field_value(elem)
                                    
                                    bulk_data.append(row_data)
                                
                                return bulk_data
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting bulk data: {e}")
            return None
    
    def get_fx_vol_surface_complete(self, currency_pair):
        """Get complete FX volatility surface with all available data"""
        
        # Build comprehensive field list
        base_ticker = f"{currency_pair} Curncy"
        
        # ATM volatility fields by tenor
        atm_fields = []
        tenors = ["1W", "2W", "1M", "2M", "3M", "6M", "9M", "1Y", "2Y"]
        
        for tenor in tenors:
            atm_fields.extend([
                f"VOLATILITY_{tenor}",
                f"FX_VOLATILITY_{tenor}",
                f"IVOL_{tenor}",
                f"ATM_VOL_{tenor}",
                f"MID_VOL_{tenor}"
            ])
        
        # Standard volatility fields
        standard_vol_fields = [
            "VOLATILITY_10D", "VOLATILITY_30D", "VOLATILITY_60D", 
            "VOLATILITY_90D", "VOLATILITY_180D", "VOLATILITY_360D",
            "IMPLIED_VOLATILITY_30D", "IMPLIED_VOLATILITY_90D"
        ]
        
        # Delta-specific fields
        delta_fields = []
        deltas = ["10", "15", "20", "25", "30", "35", "40"]
        
        for delta in deltas:
            for tenor in ["1M", "3M", "6M", "1Y"]:
                delta_fields.extend([
                    f"IVOL_{delta}D_CALL_{tenor}",
                    f"IVOL_{delta}D_PUT_{tenor}",
                    f"VOL_{delta}D_CALL_{tenor}",
                    f"VOL_{delta}D_PUT_{tenor}",
                    f"OPT_{delta}D_CALL_VOL_{tenor}",
                    f"OPT_{delta}D_PUT_VOL_{tenor}"
                ])
        
        # Risk Reversal fields
        rr_fields = []
        for delta in ["10", "25"]:
            for tenor in ["1W", "1M", "2M", "3M", "6M", "1Y"]:
                rr_fields.extend([
                    f"RISK_REVERSAL_{delta}D_{tenor}",
                    f"{delta}D_RR_{tenor}",
                    f"RR_{delta}D_{tenor}",
                    f"FX_{delta}D_RR_{tenor}",
                    f"OPT_RR_{delta}D_{tenor}"
                ])
        
        # Butterfly fields
        bf_fields = []
        for delta in ["10", "25"]:
            for tenor in ["1W", "1M", "2M", "3M", "6M", "1Y"]:
                bf_fields.extend([
                    f"BUTTERFLY_{delta}D_{tenor}",
                    f"{delta}D_BF_{tenor}",
                    f"BF_{delta}D_{tenor}",
                    f"FX_{delta}D_BF_{tenor}",
                    f"OPT_BF_{delta}D_{tenor}"
                ])
        
        # Combine all fields
        all_fields = atm_fields + standard_vol_fields + delta_fields + rr_fields + bf_fields
        
        # Remove duplicates
        all_fields = list(set(all_fields))
        
        # Get data in batches
        batch_size = 50
        all_results = {}
        
        for i in range(0, len(all_fields), batch_size):
            batch = all_fields[i:i+batch_size]
            results = self.get_reference_data([base_ticker], batch)
            
            if results and len(results) > 0:
                for field, value in results[0]["fields"].items():
                    if value is not None:
                        all_results[field] = value
        
        # Also try option tickers
        option_results = {}
        option_tenors = ["1M", "3M", "6M", "1Y"]
        
        for tenor in option_tenors:
            # ATM vol ticker
            atm_ticker = f"{currency_pair}V{tenor} Curncy"
            atm_data = self.get_reference_data([atm_ticker], ["PX_LAST", "PX_MID"])
            if atm_data and atm_data[0]["fields"].get("PX_LAST"):
                option_results[f"ATM_VOL_{tenor}"] = atm_data[0]["fields"]["PX_LAST"]
            
            # 25D option tickers
            call_ticker = f"{currency_pair}{tenor}25C Curncy"
            put_ticker = f"{currency_pair}{tenor}25P Curncy"
            
            call_data = self.get_reference_data([call_ticker], ["PX_LAST", "IMP_VOLATILITY", "IVOL_MID"])
            put_data = self.get_reference_data([put_ticker], ["PX_LAST", "IMP_VOLATILITY", "IVOL_MID"])
            
            if call_data and put_data:
                call_fields = call_data[0]["fields"]
                put_fields = put_data[0]["fields"]
                
                # Store option data
                if call_fields.get("PX_LAST"):
                    option_results[f"25D_CALL_PRICE_{tenor}"] = call_fields["PX_LAST"]
                if put_fields.get("PX_LAST"):
                    option_results[f"25D_PUT_PRICE_{tenor}"] = put_fields["PX_LAST"]
                
                # Look for implied vols
                call_vol = call_fields.get("IMP_VOLATILITY") or call_fields.get("IVOL_MID")
                put_vol = put_fields.get("IMP_VOLATILITY") or put_fields.get("IVOL_MID")
                
                if call_vol:
                    option_results[f"25D_CALL_VOL_{tenor}"] = call_vol
                if put_vol:
                    option_results[f"25D_PUT_VOL_{tenor}"] = put_vol
        
        # Try bulk data fields
        bulk_fields = ["FX_VOL_SURFACE", "OPT_VOL_MATRIX", "VOLATILITY_MATRIX"]
        bulk_results = {}
        
        for field in bulk_fields:
            bulk_data = self.get_bulk_data(base_ticker, field)
            if bulk_data:
                bulk_results[field] = bulk_data
        
        # Compile comprehensive results
        return {
            "pair": currency_pair,
            "timestamp": datetime.now().isoformat(),
            "reference_data": all_results,
            "option_data": option_results,
            "bulk_data": bulk_results,
            "fields_tested": len(all_fields),
            "fields_found": len(all_results) + len(option_results)
        }

# Initialize Bloomberg connection
bloomberg = BloombergTerminalAPI()

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "Bloomberg Terminal API Server v5.0",
        "version": "5.0",
        "bloomberg_connected": bloomberg.connected,
        "bloomberg_available": bloomberg.connected,
        "mode": "REAL_TERMINAL_FLEXIBLE"
    })

@app.route('/api/market-data', methods=['POST'])
def get_market_data():
    """Standard market data endpoint with enhanced field handling"""
    data = request.json
    securities = data.get('securities', [])
    fields = data.get('fields', [])
    overrides = data.get('overrides', {})
    
    results = bloomberg.get_reference_data(securities, fields, overrides)
    
    # Enhanced processing for vol surface fields
    for result in results:
        security = result.get("security", "")
        
        # If requesting RR/BF fields and they're null, try to calculate
        if "Curncy" in security and any("RR" in f or "BF" in f for f in fields):
            # Extract currency pair
            pair = security.replace(" Curncy", "")
            
            # Get comprehensive vol data
            vol_data = bloomberg.get_fx_vol_surface_complete(pair)
            
            # Map any found data back to requested fields
            for field in fields:
                if field in vol_data.get("reference_data", {}):
                    result["fields"][field] = vol_data["reference_data"][field]
    
    return jsonify(results)

@app.route('/api/fx/vol-surface/<pair>')
def get_vol_surface(pair):
    """Get complete volatility surface for a currency pair"""
    # Check cache first
    cache_key = f"vol_surface_{pair}"
    if cache_key in bloomberg.cache:
        cached_time, cached_data = bloomberg.cache[cache_key]
        if time.time() - cached_time < bloomberg.cache_timeout:
            return jsonify(cached_data)
    
    # Get fresh data
    result = bloomberg.get_fx_vol_surface_complete(pair.upper())
    
    # Cache the result
    bloomberg.cache[cache_key] = (time.time(), result)
    
    return jsonify(result)

@app.route('/api/fx/vol-surface/<pair>/processed')
def get_processed_vol_surface(pair):
    """Get processed volatility surface with calculated RR/BF"""
    raw_data = bloomberg.get_fx_vol_surface_complete(pair.upper())
    
    # Process the data
    processed = {
        "pair": pair.upper(),
        "timestamp": datetime.now().isoformat(),
        "atmVols": {},
        "riskReversals": {"25D": {}, "10D": {}},
        "butterflies": {"25D": {}, "10D": {}},
        "raw_fields_found": raw_data.get("fields_found", 0)
    }
    
    # Extract ATM vols
    for tenor in ["1M", "3M", "6M", "1Y"]:
        # Check multiple possible field names
        atm_value = None
        
        # From option data
        if f"ATM_VOL_{tenor}" in raw_data.get("option_data", {}):
            atm_value = raw_data["option_data"][f"ATM_VOL_{tenor}"]
        
        # From reference data
        if not atm_value:
            for field_pattern in [f"VOLATILITY_{tenor}", f"FX_VOLATILITY_{tenor}", f"IVOL_{tenor}"]:
                if field_pattern in raw_data.get("reference_data", {}):
                    atm_value = raw_data["reference_data"][field_pattern]
                    break
        
        if atm_value:
            processed["atmVols"][tenor] = atm_value
    
    # Extract or calculate RR/BF
    for tenor in ["1M", "3M", "6M", "1Y"]:
        # Try to find direct RR/BF values
        rr_25d = None
        bf_25d = None
        
        # Check for direct RR fields
        for rr_pattern in [f"25D_RR_{tenor}", f"RISK_REVERSAL_25D_{tenor}", f"FX_25D_RR_{tenor}"]:
            if rr_pattern in raw_data.get("reference_data", {}):
                rr_25d = raw_data["reference_data"][rr_pattern]
                break
        
        # Check for direct BF fields
        for bf_pattern in [f"25D_BF_{tenor}", f"BUTTERFLY_25D_{tenor}", f"FX_25D_BF_{tenor}"]:
            if bf_pattern in raw_data.get("reference_data", {}):
                bf_25d = raw_data["reference_data"][bf_pattern]
                break
        
        # If not found, try to calculate from call/put vols
        if not rr_25d:
            call_vol = raw_data.get("option_data", {}).get(f"25D_CALL_VOL_{tenor}")
            put_vol = raw_data.get("option_data", {}).get(f"25D_PUT_VOL_{tenor}")
            
            if call_vol and put_vol:
                rr_25d = call_vol - put_vol
        
        if not bf_25d and rr_25d is not None:
            call_vol = raw_data.get("option_data", {}).get(f"25D_CALL_VOL_{tenor}")
            put_vol = raw_data.get("option_data", {}).get(f"25D_PUT_VOL_{tenor}")
            atm_vol = processed["atmVols"].get(tenor)
            
            if call_vol and put_vol and atm_vol:
                bf_25d = 0.5 * (call_vol + put_vol) - atm_vol
        
        # Store results
        if rr_25d is not None:
            processed["riskReversals"]["25D"][tenor] = rr_25d
        if bf_25d is not None:
            processed["butterflies"]["25D"][tenor] = bf_25d
    
    return jsonify(processed)

@app.route('/api/discover/<security>')
def discover_fields(security):
    """Discover all available fields for a security"""
    # Common FX vol fields to test
    test_fields = [
        "PX_LAST", "PX_MID", "PX_BID", "PX_ASK",
        "VOLATILITY_10D", "VOLATILITY_30D", "VOLATILITY_60D", "VOLATILITY_90D",
        "VOLATILITY_180D", "VOLATILITY_360D", "IMPLIED_VOLATILITY",
        "IMP_VOLATILITY", "IVOL_MID", "OPT_IMPLIED_VOLATILITY"
    ]
    
    results = bloomberg.get_reference_data([security], test_fields)
    
    if results:
        found_fields = {k: v for k, v in results[0]["fields"].items() if v is not None}
        return jsonify({
            "security": security,
            "fields_tested": len(test_fields),
            "fields_found": len(found_fields),
            "available_fields": found_fields
        })
    
    return jsonify({"error": "No data found"}), 404

@app.route('/api/fx/rates')
def get_fx_rates():
    """Get FX rates"""
    pairs = request.args.getlist('pairs') or ["EURUSD", "GBPUSD", "USDJPY"]
    securities = [f"{pair} Curncy" for pair in pairs]
    fields = ["PX_LAST", "PX_BID", "PX_ASK", "CHG_PCT_1D", "VOLATILITY_90D"]
    
    results = bloomberg.get_reference_data(securities, fields)
    return jsonify(results)

if __name__ == '__main__':
    if bloomberg.connected:
        logger.info("Starting Bloomberg Terminal API Server v5.0 on port 8080")
        logger.info("Enhanced with comprehensive FX volatility surface extraction")
        app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        logger.error("Failed to connect to Bloomberg Terminal")
        sys.exit(1)