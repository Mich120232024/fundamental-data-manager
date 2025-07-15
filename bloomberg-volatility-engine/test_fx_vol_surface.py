#!/usr/bin/env python3
"""
Test FX Volatility Surface Data from Bloomberg
Discover what's needed to rebuild historical volatility surfaces
"""

import requests
import json
from datetime import datetime
import pandas as pd

def test_fx_volatility_surface():
    """Test all volatility surface components available in Bloomberg"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 FX VOLATILITY SURFACE DATA DISCOVERY")
    print("=" * 60)
    
    # Test multiple currency pairs
    fx_pairs = ["EURUSD Curncy", "GBPUSD Curncy", "USDJPY Curncy"]
    
    # 1. Test basic volatility fields we know work
    print("\n1. TESTING KNOWN VOLATILITY FIELDS:")
    print("-" * 40)
    
    known_vol_fields = [
        "PX_LAST",
        "VOLATILITY_30D",
        "VOLATILITY_90D",
        "VOLATILITY_180D",
        "VOLATILITY_360D"
    ]
    
    for pair in fx_pairs[:1]:  # Test EURUSD first
        response = requests.post(
            f"{base_url}/api/market-data",
            json={"securities": [pair], "fields": known_vol_fields}
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            print(f"\n{pair}:")
            for field, value in data['fields'].items():
                print(f"  {field}: {value}")
    
    # 2. Test volatility smile components
    print("\n\n2. TESTING VOLATILITY SMILE/SKEW FIELDS:")
    print("-" * 40)
    
    smile_fields = [
        # Risk Reversals (25 delta)
        "25D_RR_1M", "25D_RR_3M", "25D_RR_6M", "25D_RR_1Y",
        "1M_25D_RR", "3M_25D_RR", "6M_25D_RR",
        "RISK_REVERSAL_25D_1M", "RISK_REVERSAL_25D_3M",
        
        # Butterflies (25 delta)
        "25D_BF_1M", "25D_BF_3M", "25D_BF_6M",
        "1M_25D_BF", "3M_25D_BF",
        "BUTTERFLY_25D_1M", "BUTTERFLY_25D_3M",
        
        # 10 delta risk reversals
        "10D_RR_1M", "10D_RR_3M",
        "RISK_REVERSAL_10D_1M",
        
        # ATM vols by tenor
        "1M_ATM_VOL", "3M_ATM_VOL", "6M_ATM_VOL", "1Y_ATM_VOL",
        "ATM_1M_IMP_VOL", "ATM_3M_IMP_VOL"
    ]
    
    # Test in batches to avoid timeout
    batch_size = 5
    found_smile_fields = {}
    
    for i in range(0, len(smile_fields), batch_size):
        batch = smile_fields[i:i+batch_size]
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": ["EURUSD Curncy"], "fields": batch},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                for field, value in data['fields'].items():
                    if value is not None:
                        found_smile_fields[field] = value
                        print(f"  ✓ Found: {field} = {value}")
        except:
            pass
    
    # 3. Test volatility surface points
    print("\n\n3. TESTING SPECIFIC VOLATILITY SURFACE POINTS:")
    print("-" * 40)
    
    # Try different delta/tenor combinations
    surface_fields = [
        # Format variations for 25 delta puts/calls
        "1M_25DP_VOL", "1M_25DC_VOL",
        "3M_25DP_VOL", "3M_25DC_VOL",
        "EUR1M25P", "EUR1M25C",
        "EURUSD_1M_25P_VOL", "EURUSD_1M_25C_VOL",
        
        # Different deltas
        "1M_10D_VOL", "1M_35D_VOL", "1M_40D_VOL",
        
        # Strangles/straddles
        "1M_STRANGLE_25D", "3M_STRANGLE_25D",
        "1M_ATM_STRADDLE", "3M_ATM_STRADDLE"
    ]
    
    for field in surface_fields[:10]:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": ["EURUSD Curncy"], "fields": [field]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                if field in data['fields'] and data['fields'][field] is not None:
                    print(f"  ✓ {field}: {data['fields'][field]}")
        except:
            pass
    
    # 4. Test option tickers directly
    print("\n\n4. TESTING FX OPTION TICKERS:")
    print("-" * 40)
    
    option_tickers = [
        # Standard option vol tickers
        "EURUSDV1M Curncy",  # 1-month vol
        "EURUSDV3M Curncy",  # 3-month vol
        "EURUSDV6M Curncy",  # 6-month vol
        "EURUSDV1Y Curncy",  # 1-year vol
        
        # Specific strikes
        "EUR1M Curncy",      # 1-month ATM
        "EUR3M Curncy",      # 3-month ATM
        "EUR1M25C Curncy",   # 1-month 25-delta call
        "EUR1M25P Curncy",   # 1-month 25-delta put
    ]
    
    for ticker in option_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID"]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]['fields']:
                    fields = data[0]['fields']
                    if any(fields.values()):
                        print(f"  ✓ {ticker}: {fields}")
        except:
            pass
    
    # 5. Summary and recommendations
    print("\n\n" + "=" * 60)
    print("📊 VOLATILITY SURFACE RECONSTRUCTION ANALYSIS")
    print("=" * 60)
    
    print("\nAVAILABLE DATA:")
    print("  ✓ Basic implied volatilities (30D, 90D, 180D, 360D)")
    if found_smile_fields:
        print("  ✓ Smile components found:")
        for field in found_smile_fields:
            print(f"    - {field}")
    
    print("\nTO BUILD VOLATILITY SURFACE YOU NEED:")
    print("  1. ATM volatilities for each tenor (1W, 2W, 1M, 2M, 3M, 6M, 9M, 1Y)")
    print("  2. Risk reversals (25D, 10D) for each tenor")
    print("  3. Butterflies (25D, 10D) for each tenor")
    print("  4. Spot rate and forward points")
    
    print("\nVOLATILITY SURFACE FORMULA:")
    print("  σ(K,T) = σ_ATM(T) + RR(T) × δ(K) + BF(T) × δ(K)²")
    print("  where:")
    print("  - σ_ATM = ATM volatility for tenor T")
    print("  - RR = Risk Reversal (σ_25D_Call - σ_25D_Put)")
    print("  - BF = Butterfly (σ_25D - σ_ATM)")
    print("  - δ(K) = Delta of option with strike K")


if __name__ == "__main__":
    test_fx_volatility_surface()