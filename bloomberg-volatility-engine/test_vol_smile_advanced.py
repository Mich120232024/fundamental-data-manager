#!/usr/bin/env python3
"""
Advanced test for FX volatility smile components
Testing specific Bloomberg fields for risk reversals and butterflies
"""

import requests
import json
from datetime import datetime

def test_advanced_vol_smile():
    """Test more specific Bloomberg fields for vol smile data"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 ADVANCED VOLATILITY SMILE DATA DISCOVERY")
    print("=" * 60)
    
    # Test different currency pairs and tenors
    fx_pairs = ["EURUSD Curncy", "GBPUSD Curncy", "USDJPY Curncy"]
    
    # 1. Test specific Bloomberg vol smile fields
    print("\n1. TESTING BLOOMBERG-SPECIFIC VOL FIELDS:")
    print("-" * 40)
    
    bloomberg_vol_fields = [
        # Standard Bloomberg vol surface fields
        "IVOL_DELTA_25_CALL_1M",
        "IVOL_DELTA_25_PUT_1M", 
        "IVOL_DELTA_10_CALL_1M",
        "IVOL_DELTA_10_PUT_1M",
        "IVOL_ATM_1M",
        
        # Risk reversal specific
        "25_DELTA_RISK_REVERSAL_1M",
        "10_DELTA_RISK_REVERSAL_1M",
        
        # Butterfly specific
        "25_DELTA_BUTTERFLY_1M",
        "10_DELTA_BUTTERFLY_1M",
        
        # Alternative formats
        "FX_25D_RR_1M",
        "FX_25D_BF_1M",
        "FX_ATM_VOL_1M",
        
        # Vol smile parameters
        "VOLATILITY_SMILE_25D_1M",
        "VOLATILITY_SKEW_1M",
        
        # Quoted spreads
        "25_DELTA_VOL_SPREAD_1M",
        "ATM_25_DELTA_VOL_SPREAD_1M"
    ]
    
    # Test in small batches
    found_fields = {}
    batch_size = 4
    
    for pair in fx_pairs[:1]:  # Test EURUSD first
        print(f"\nTesting {pair}:")
        for i in range(0, len(bloomberg_vol_fields), batch_size):
            batch = bloomberg_vol_fields[i:i+batch_size]
            try:
                response = requests.post(
                    f"{base_url}/api/market-data",
                    json={"securities": [pair], "fields": batch},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()[0]
                    for field, value in data['fields'].items():
                        if value is not None:
                            found_fields[field] = value
                            print(f"  ✓ {field}: {value}")
            except Exception as e:
                pass
    
    # 2. Test option-specific tickers
    print("\n\n2. TESTING FX OPTION VOL TICKERS:")
    print("-" * 40)
    
    option_vol_tickers = [
        # Standard vol tickers by tenor
        "EURUSDV1W Curncy",  # 1 week
        "EURUSDV2W Curncy",  # 2 week
        "EURUSDV1M Curncy",  # 1 month
        "EURUSDV2M Curncy",  # 2 month
        "EURUSDV3M Curncy",  # 3 month
        "EURUSDV6M Curncy",  # 6 month
        "EURUSDV9M Curncy",  # 9 month
        "EURUSDV1Y Curncy",  # 1 year
        
        # Risk reversal tickers
        "EUR25R1M Curncy",   # 25 delta RR 1M
        "EUR10R1M Curncy",   # 10 delta RR 1M
        "EUR25R3M Curncy",   # 25 delta RR 3M
        
        # Butterfly tickers
        "EUR25B1M Curncy",   # 25 delta BF 1M
        "EUR10B1M Curncy",   # 10 delta BF 1M
        "EUR25B3M Curncy",   # 25 delta BF 3M
        
        # Strangle/specific strikes
        "EUR25C1M Curncy",   # 25 delta call 1M
        "EUR25P1M Curncy",   # 25 delta put 1M
        "EUR10C1M Curncy",   # 10 delta call 1M
        "EUR10P1M Curncy"    # 10 delta put 1M
    ]
    
    vol_surface_data = {}
    
    for ticker in option_vol_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID", "PX_BID", "PX_ASK"]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]['fields']:
                    fields = data[0]['fields']
                    if any(v is not None for v in fields.values()):
                        vol_surface_data[ticker] = fields
                        print(f"  ✓ {ticker}: {fields}")
        except:
            pass
    
    # 3. Test volatility surface points with specific field combinations
    print("\n\n3. TESTING COMBINED FIELD APPROACH:")
    print("-" * 40)
    
    # Try to calculate smile components from individual vols
    test_combos = [
        {
            "description": "ATM and wing vols",
            "securities": ["EURUSD Curncy"],
            "fields": ["VOLATILITY_30D", "VOLATILITY_90D", "IMPLIED_VOLATILITY_MID"]
        },
        {
            "description": "Option premiums for different strikes",
            "securities": ["EUR1M Curncy", "EUR3M Curncy", "EUR6M Curncy"],
            "fields": ["PX_LAST", "DELTA", "IMPLIED_VOLATILITY"]
        }
    ]
    
    for test in test_combos:
        print(f"\n{test['description']}:")
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json=test,
                timeout=10
            )
            if response.status_code == 200:
                print(f"  Response: {json.dumps(response.json(), indent=2)}")
        except:
            pass
    
    # 4. Analysis and recommendations
    print("\n\n" + "=" * 60)
    print("📊 VOLATILITY SURFACE RECONSTRUCTION FEASIBILITY")
    print("=" * 60)
    
    print("\nAVAILABLE DATA SUMMARY:")
    print("  ✓ ATM implied vols by tenor (1W to 1Y)")
    print("  ✓ Basic historical volatility (30D, 90D, etc)")
    print("  ✓ Spot FX rates with bid/ask")
    
    if found_fields:
        print("\n  ✓ Additional smile fields found:")
        for field, value in found_fields.items():
            print(f"    - {field}: {value}")
    
    if vol_surface_data:
        print("\n  ✓ Vol surface tickers available:")
        tenors = ["1W", "2W", "1M", "2M", "3M", "6M", "9M", "1Y"]
        for tenor in tenors:
            ticker = f"EURUSDV{tenor} Curncy"
            if ticker in vol_surface_data:
                print(f"    - {tenor}: {vol_surface_data[ticker]}")
    
    print("\nRECOMMENDED APPROACH:")
    print("  1. Collect ATM vols for all tenors (working)")
    print("  2. Use vol surface interpolation for missing smile data")
    print("  3. Store daily snapshots for historical analysis")
    print("  4. Implement SABR or SVI model for smile interpolation")
    
    print("\nDATA COLLECTION SCRIPT:")
    print("  - Run every market day at fixed time")
    print("  - Collect: Spot, ATM vols (all tenors), any available RR/BF")
    print("  - Store in structured format for surface fitting")
    print("  - Build analytics on top of collected data")


if __name__ == "__main__":
    test_advanced_vol_smile()