#!/usr/bin/env python3
"""
Comprehensive test of ALL possible FX option volatility fields
This will help identify what fields the Terminal actually provides
"""

import requests
import json
from datetime import datetime
import time

def test_all_volatility_fields():
    """Test every possible volatility field combination"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🔍 COMPREHENSIVE FX VOLATILITY FIELD DISCOVERY")
    print("=" * 60)
    print(f"Testing ALL possible field combinations at {datetime.now()}")
    print("=" * 60)
    
    # Comprehensive list of potential volatility fields
    all_possible_fields = [
        # Standard volatility fields
        "VOLATILITY_30D", "VOLATILITY_60D", "VOLATILITY_90D", "VOLATILITY_180D", "VOLATILITY_360D",
        "IVOL_MID", "IMP_VOLATILITY", "IMPLIED_VOLATILITY",
        
        # Option specific
        "OPT_IMPLIED_VOLATILITY", "OPT_DELTA_MID_VOL", "OPT_DELTA_NEUTRAL_MID_VOL",
        
        # Call/Put specific vols
        "OPT_25D_CALL_IMP_VOL", "OPT_25D_PUT_IMP_VOL",
        "OPT_10D_CALL_IMP_VOL", "OPT_10D_PUT_IMP_VOL",
        "OPT_ATM_IMP_VOL",
        
        # FX specific
        "FX_IMPLIED_VOL", "FX_VOLATILITY", "FX_OPT_VOL",
        "FX_25D_CALL_VOL", "FX_25D_PUT_VOL",
        
        # Risk Reversal variations
        "RISK_REVERSAL", "RISK_REVERSAL_25D", "RISK_REVERSAL_10D",
        "25D_RISK_REVERSAL", "10D_RISK_REVERSAL",
        "OPT_25D_RR", "OPT_10D_RR",
        "FX_25D_RR", "FX_10D_RR",
        "DELTA_25_RR", "DELTA_10_RR",
        
        # Butterfly variations
        "BUTTERFLY", "BUTTERFLY_25D", "BUTTERFLY_10D",
        "25D_BUTTERFLY", "10D_BUTTERFLY",
        "OPT_25D_BF", "OPT_10D_BF",
        "FX_25D_BF", "FX_10D_BF",
        "DELTA_25_BF", "DELTA_10_BF",
        
        # Strangle/Smile
        "STRANGLE_25D", "SMILE_25D",
        "VOL_SMILE_25D", "VOL_SMILE_10D",
        
        # Surface specific
        "VOL_SURFACE", "IVOL_SURFACE", "OPT_VOL_SURFACE",
        "VOLATILITY_SURFACE_MID",
        
        # OVDV specific
        "OVDV_ATM_VOL", "OVDV_25D_VOL", "OVDV_RR", "OVDV_BF",
        
        # Matrix fields
        "VOLATILITY_MATRIX", "OPT_VOLATILITY_MATRIX",
        
        # With tenor suffixes
        "VOLATILITY_1M", "VOLATILITY_3M", "VOLATILITY_6M", "VOLATILITY_1Y",
        "RISK_REVERSAL_25D_1M", "RISK_REVERSAL_25D_3M",
        "BUTTERFLY_25D_1M", "BUTTERFLY_25D_3M"
    ]
    
    # Test in batches
    batch_size = 10
    found_fields = {}
    
    print("\n1. TESTING ON EURUSD BASE TICKER:")
    print("-" * 40)
    
    for i in range(0, len(all_possible_fields), batch_size):
        batch = all_possible_fields[i:i+batch_size]
        
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": ["EURUSD Curncy"], "fields": batch},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                for field, value in data['fields'].items():
                    if value is not None:
                        found_fields[field] = value
                        print(f"  ✓ FOUND: {field} = {value}")
            
            time.sleep(0.5)  # Be nice to the API
            
        except Exception as e:
            print(f"  ⚠️  Batch error: {e}")
    
    # Test option-specific tickers
    print("\n\n2. TESTING OPTION TICKERS WITH VOL FIELDS:")
    print("-" * 40)
    
    option_tickers = [
        "EURUSD1M Curncy",
        "EUR1M Curncy",
        "EURUSD1M25C Curncy",
        "EURUSD1M25P Curncy"
    ]
    
    vol_fields = [
        "IMP_VOLATILITY", "IMPLIED_VOLATILITY", "IVOL_MID",
        "OPT_IMPLIED_VOLATILITY", "VOLATILITY_MID"
    ]
    
    for ticker in option_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": vol_fields},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                non_null = {k: v for k, v in data['fields'].items() if v is not None}
                if non_null:
                    print(f"\n  {ticker}:")
                    for field, value in non_null.items():
                        print(f"    {field}: {value}")
        except:
            pass
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 DISCOVERY RESULTS")
    print("=" * 60)
    
    if found_fields:
        print(f"\n✅ FOUND {len(found_fields)} WORKING FIELDS:")
        
        # Categorize findings
        atm_fields = {k: v for k, v in found_fields.items() if "RR" not in k and "BF" not in k and "BUTTERFLY" not in k}
        rr_fields = {k: v for k, v in found_fields.items() if "RR" in k or "REVERSAL" in k}
        bf_fields = {k: v for k, v in found_fields.items() if "BF" in k or "BUTTERFLY" in k}
        
        if atm_fields:
            print("\n  ATM Volatility Fields:")
            for field, value in atm_fields.items():
                print(f"    - {field}: {value}")
        
        if rr_fields:
            print("\n  Risk Reversal Fields:")
            for field, value in rr_fields.items():
                print(f"    - {field}: {value}")
        
        if bf_fields:
            print("\n  Butterfly Fields:")
            for field, value in bf_fields.items():
                print(f"    - {field}: {value}")
    else:
        print("\n❌ NO VOLATILITY FIELDS FOUND")
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Fields found here ARE available through the Terminal")
    print("2. If no RR/BF fields found, Terminal may need:")
    print("   - Different field names")
    print("   - OVDV screen access")
    print("   - Excel Add-in API")
    print("3. Consider using BDH() function for historical vol surface")


if __name__ == "__main__":
    test_all_volatility_fields()