#!/usr/bin/env python3
"""
Focused test on EURUSD to understand option data structure
"""

import requests
import json
from datetime import datetime

def test_single_eurusd():
    """Test EURUSD option data in detail"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 EURUSD SINGLE CURRENCY ANALYSIS")
    print("=" * 60)
    
    # Test 1: Get all available data for 1M options
    print("\n1. EURUSD 1-MONTH OPTIONS ANALYSIS:")
    print("-" * 40)
    
    # Request all available fields
    all_fields = [
        "PX_LAST", "PX_MID", "PX_BID", "PX_ASK",
        "IMP_VOLATILITY", "IVOL_MID", "OPT_IMPLIED_VOLATILITY",
        "DELTA", "DELTA_MID", "OPT_DELTA_MID",
        "STRIKE", "DAYS_TO_EXPIRY", "OPT_EXPIRE_DT",
        "OPT_PUT_CALL", "OPT_CONT_SIZE",
        "VOLATILITY_MID", "VOLATILITY_BID", "VOLATILITY_ASK"
    ]
    
    option_tickers = [
        "EURUSDV1M Curncy",   # ATM vol
        "EURUSD1M25C Curncy", # 25-delta call
        "EURUSD1M25P Curncy", # 25-delta put
    ]
    
    for ticker in option_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": all_fields},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                print(f"\n{ticker}:")
                print(f"  Security type: {data.get('security_type', 'Unknown')}")
                
                # Print all non-null fields
                fields = data.get('fields', {})
                for field, value in fields.items():
                    if value is not None:
                        print(f"  {field}: {value}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test 2: Analyze the 24.14 value
    print("\n\n2. ANALYZING THE 24.14 VALUE:")
    print("-" * 40)
    
    # If 24.14 is volatility, let's calculate what RR and BF would be
    atm_vol = 7.6375  # From EURUSDV1M
    option_vol = 24.14  # From both call and put
    
    print(f"ATM Vol (EURUSDV1M): {atm_vol}%")
    print(f"Option value (25C/25P): {option_vol}")
    print(f"\nIf {option_vol} is volatility:")
    print(f"  - Risk Reversal = 0 (same vol for call and put)")
    print(f"  - 25D vol would be significantly higher than ATM")
    print(f"  - This seems unlikely (25D vol = 3x ATM vol?)")
    print(f"\nIf {option_vol} is price in pips:")
    print(f"  - Would represent option premium")
    print(f"  - Same price for call and put suggests ATM forward")
    
    # Test 3: Try specific smile fields
    print("\n\n3. TESTING SMILE-SPECIFIC FIELDS:")
    print("-" * 40)
    
    smile_fields = [
        "SMILE_VOL_25D_MS",
        "SMILE_VOL_25D_RR", 
        "SMILE_VOL_25D_BF",
        "FX_25D_RR",
        "FX_25D_BF",
        "OPT_25D_RR",
        "OPT_25D_BF"
    ]
    
    try:
        response = requests.post(
            f"{base_url}/api/market-data",
            json={"securities": ["EURUSD Curncy"], "fields": smile_fields},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            print("Testing smile fields on EURUSD Curncy:")
            found_any = False
            for field, value in data['fields'].items():
                if value is not None:
                    print(f"  ✓ {field}: {value}")
                    found_any = True
            if not found_any:
                print("  ✗ No smile fields available")
    except Exception as e:
        print(f"Error: {e}")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 CONCLUSIONS FOR EURUSD")
    print("=" * 60)
    print("\n1. ATM volatilities are clearly available (EURUSDV[tenor])")
    print("2. Option tickers EURUSD1M25C/P return identical values (24.14)")
    print("3. This value is likely option premium, not implied volatility")
    print("4. Bloomberg Terminal may not provide individual strike volatilities")
    print("5. Risk Reversals and Butterflies not available as direct fields")
    
    print("\n🎯 RECOMMENDATION:")
    print("For now, implement flat volatility surface using only ATM data")
    print("This is market standard when smile data is unavailable")


if __name__ == "__main__":
    test_single_eurusd()