#!/usr/bin/env python3
"""
Test Bloomberg Terminal OVDV (Option Volatility) functionality
The Terminal has different screens for accessing option data
"""

import requests
import json
from datetime import datetime

def test_terminal_ovdv():
    """Test Terminal-specific option volatility access"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 BLOOMBERG TERMINAL OVDV SCREEN EMULATION")
    print("=" * 60)
    print("Testing Terminal-specific option volatility fields")
    print("=" * 60)
    
    # Terminal OVDV screen uses these fields
    print("\n1. TESTING OVDV SCREEN FIELDS:")
    print("-" * 40)
    
    ovdv_fields = [
        # Standard OVDV fields
        "IVOL_DELTA_25_CALL",
        "IVOL_DELTA_25_PUT",
        "IVOL_DELTA_10_CALL", 
        "IVOL_DELTA_10_PUT",
        "IVOL_ATM",
        "IVOL_DELTA_NEUTRAL",
        
        # Risk Reversal/Butterfly as direct fields
        "RISK_REVERSAL_25_DELTA",
        "BUTTERFLY_25_DELTA",
        "RISK_REVERSAL_10_DELTA",
        "BUTTERFLY_10_DELTA",
        
        # Volatility surface points
        "VOL_SURF_DELTA_25_CALL",
        "VOL_SURF_DELTA_25_PUT",
        "VOL_SURF_ATM",
        
        # FX specific vol fields
        "FX_VOLATILITY_25D_CALL",
        "FX_VOLATILITY_25D_PUT",
        "FX_IMPLIED_VOL_ATM"
    ]
    
    # Test on base currency pair
    try:
        response = requests.post(
            f"{base_url}/api/market-data",
            json={"securities": ["EURUSD Curncy"], "fields": ovdv_fields},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            print("EURUSD Curncy - OVDV fields:")
            found = False
            for field, value in data['fields'].items():
                if value is not None:
                    print(f"  ✓ {field}: {value}")
                    found = True
            if not found:
                print("  ✗ No OVDV fields available")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Try accessing through volatility surface ticker
    print("\n\n2. TESTING VOLATILITY SURFACE TICKERS:")
    print("-" * 40)
    
    surface_tickers = [
        "EURUSD OVDV Curncy",     # Option vol surface
        "EURUSD VOLC Curncy",     # Vol curve
        "EURUSD IVOL Curncy",     # Implied vol
        "EURUSD VOL Curncy",      # Generic vol
        "EURUSDVOL Index",        # Vol index
        "EURUSD OVML Curncy"      # Option vol model
    ]
    
    for ticker in surface_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST", "IVOL_MID"]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                fields = data.get('fields', {})
                if any(v is not None for v in fields.values()):
                    print(f"  ✓ {ticker}: {fields}")
        except:
            pass
    
    # Test 3: Terminal-specific FX option chain
    print("\n\n3. TESTING FX OPTION CHAIN ACCESS:")
    print("-" * 40)
    
    # Terminal uses specific syntax for option chains
    chain_requests = [
        {
            "security": "EURUSD Curncy",
            "fields": ["OPT_CHAIN", "OPT_VOLATILITY_SURFACE"]
        },
        {
            "security": "EUR Curncy", 
            "fields": ["OPT_VOLATILITY_MATRIX", "OPT_SMILE_DATA"]
        }
    ]
    
    for req in chain_requests:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [req["security"]], "fields": req["fields"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                print(f"\n{req['security']}:")
                for field in req["fields"]:
                    value = data['fields'].get(field)
                    if value is not None:
                        print(f"  ✓ {field}: {value}")
                    else:
                        print(f"  ✗ {field}: null")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test 4: Check if we need to use OVDV function
    print("\n\n4. TERMINAL FUNCTION COMMANDS:")
    print("-" * 40)
    print("In Bloomberg Terminal, FX option volatilities are accessed via:")
    print("  - EURUSD Curncy OVDV <GO> - Option Volatility Surface")
    print("  - EURUSD Curncy OVML <GO> - Option Volatility Model")
    print("  - FXO <GO> - FX Options")
    print("\nThe API might need special handling for these screens")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 TERMINAL ACCESS RECOMMENDATIONS")
    print("=" * 60)
    print("\n1. Bloomberg Terminal HAS the data (visible in OVDV screen)")
    print("2. API server might need enhancement to expose OVDV data")
    print("3. Consider using Terminal's Excel API (BDH/BDS functions)")
    print("4. Or update the API server to handle OVDV screen scraping")


if __name__ == "__main__":
    test_terminal_ovdv()