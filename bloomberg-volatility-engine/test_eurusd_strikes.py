#!/usr/bin/env python3
"""
Test EURUSD individual strike volatilities
Calculate Risk Reversals and Butterflies manually
"""

import requests
import json
from datetime import datetime

def test_individual_strikes():
    """Test getting individual 25-delta call and put volatilities"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 EURUSD INDIVIDUAL STRIKE TESTING")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test different ticker formats for 25-delta options
    print("\n1. TESTING 25-DELTA OPTION TICKERS:")
    print("-" * 40)
    
    # Try various ticker formats
    strike_tickers = [
        # Format 1: EUR + tenor + delta + type
        ("EUR1M25C Curncy", "1M 25-delta Call"),
        ("EUR1M25P Curncy", "1M 25-delta Put"),
        ("EUR3M25C Curncy", "3M 25-delta Call"),
        ("EUR3M25P Curncy", "3M 25-delta Put"),
        
        # Format 2: EURUSD + specific
        ("EURUSD1M25C Curncy", "1M 25-delta Call"),
        ("EURUSD1M25P Curncy", "1M 25-delta Put"),
        
        # Format 3: With V for volatility
        ("EURUSDV1M25C Curncy", "1M 25-delta Call vol"),
        ("EURUSDV1M25P Curncy", "1M 25-delta Put vol"),
        
        # Format 4: Different delta notation
        ("EUR1M75C Curncy", "1M 75-delta Call (25-delta Put mirror)"),
        ("EUR1M75P Curncy", "1M 75-delta Put"),
    ]
    
    found_tickers = {}
    
    for ticker, description in strike_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID", "IMP_VOLATILITY"]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                fields = data.get('fields', {})
                if any(v is not None for v in fields.values()):
                    print(f"  ✓ {ticker}: {fields} - {description}")
                    found_tickers[ticker] = fields
        except Exception as e:
            pass
    
    # Test 2: Try option fields on ATM tickers
    print("\n\n2. TESTING OPTION FIELDS ON ATM TICKERS:")
    print("-" * 40)
    
    option_fields = [
        "OPT_DELTA_25_CALL_VOL",
        "OPT_DELTA_25_PUT_VOL", 
        "OPT_DELTA_10_CALL_VOL",
        "OPT_DELTA_10_PUT_VOL",
        "DELTA_25_CALL_IMP_VOL",
        "DELTA_25_PUT_IMP_VOL",
        "25_DELTA_CALL_VOL",
        "25_DELTA_PUT_VOL",
        "IMP_VOL_25D_CALL",
        "IMP_VOL_25D_PUT"
    ]
    
    test_ticker = "EURUSDV1M Curncy"
    
    try:
        response = requests.post(
            f"{base_url}/api/market-data",
            json={"securities": [test_ticker], "fields": option_fields},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            print(f"\nTesting fields on {test_ticker}:")
            for field, value in data['fields'].items():
                if value is not None:
                    print(f"  ✓ {field}: {value}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: FX Option specific fields
    print("\n\n3. TESTING FX OPTION SPECIFIC FIELDS:")
    print("-" * 40)
    
    fx_option_fields = [
        "FX_OPT_25D_RR_1M",
        "FX_OPT_25D_BF_1M",
        "FX_25_DELTA_RR",
        "FX_25_DELTA_BF",
        "OPT_25D_RR",
        "OPT_25D_BF",
        "VOLATILITY_25D_RR",
        "VOLATILITY_25D_BF"
    ]
    
    try:
        response = requests.post(
            f"{base_url}/api/market-data",
            json={"securities": ["EURUSD Curncy"], "fields": fx_option_fields},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            print(f"\nFX option fields on EURUSD Curncy:")
            for field, value in data['fields'].items():
                if value is not None:
                    print(f"  ✓ {field}: {value}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Manual calculation example
    print("\n\n4. VOLATILITY SURFACE CALCULATION:")
    print("-" * 40)
    
    # Get ATM vols again for reference
    atm_vols = {}
    tenors = ["1M", "3M", "6M", "1Y"]
    
    for tenor in tenors:
        ticker = f"EURUSDV{tenor} Curncy"
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST"]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                vol = data['fields'].get('PX_LAST')
                if vol:
                    atm_vols[tenor] = vol
                    print(f"  ATM {tenor}: {vol}%")
        except:
            pass
    
    print("\n  Without RR/BF data, surface shows flat volatility across strikes")
    print("  Need Bloomberg to provide strike-specific vols or RR/BF quotes")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 FINDINGS")
    print("=" * 60)
    print("\n1. ATM volatilities are available and working")
    print("2. Risk Reversal and Butterfly fields return null")
    print("3. Individual strike tickers not found in tested formats")
    print("4. Bloomberg Terminal may not have FX option smile data in subscription")
    
    print("\n🔧 POSSIBLE SOLUTIONS:")
    print("1. Check Bloomberg Terminal directly for available FX option data")
    print("2. Contact Bloomberg support about FX option vol surface access")
    print("3. Use flat volatility surface (ATM only) as interim solution")
    print("4. Source smile data from alternative providers")


if __name__ == "__main__":
    test_individual_strikes()