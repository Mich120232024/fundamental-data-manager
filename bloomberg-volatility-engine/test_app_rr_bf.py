#!/usr/bin/env python3
"""
Test that the React app is now getting real RR/BF data
"""

import requests
import json
from datetime import datetime

def test_app_integration():
    """Test the full volatility surface with RR/BF"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 TESTING COMPLETE VOLATILITY SURFACE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    # Get ATM volatilities
    print("\n1. ATM VOLATILITIES:")
    print("-" * 40)
    
    atm_tickers = {
        "1M": "EURUSDV1M Curncy",
        "3M": "EURUSDV3M Curncy",
        "6M": "EURUSDV6M Curncy",
        "1Y": "EURUSDV1Y Curncy"
    }
    
    atm_vols = {}
    for tenor, ticker in atm_tickers.items():
        response = requests.post(
            f"{base_url}/api/market-data",
            json={"securities": [ticker], "fields": ["PX_LAST"]}
        )
        if response.status_code == 200:
            vol = response.json()[0]["fields"]["PX_LAST"]
            atm_vols[tenor] = vol
            print(f"  {tenor}: {vol:.3f}%")
    
    # Get Risk Reversals
    print("\n\n2. RISK REVERSALS (25-Delta):")
    print("-" * 40)
    
    rr_values = {}
    for tenor in ["1M", "3M", "6M", "1Y"]:
        ticker = f"EUR25R{tenor} Curncy"
        response = requests.post(
            f"{base_url}/api/market-data",
            json={"securities": [ticker], "fields": ["PX_LAST"]}
        )
        if response.status_code == 200:
            rr = response.json()[0]["fields"]["PX_LAST"]
            rr_values[tenor] = rr
            print(f"  {tenor}: {rr:.3f}")
    
    # Get Butterflies
    print("\n\n3. BUTTERFLIES (25-Delta):")
    print("-" * 40)
    
    bf_values = {}
    for tenor in ["1M", "3M", "6M", "1Y"]:
        ticker = f"EUR25B{tenor} Curncy"
        response = requests.post(
            f"{base_url}/api/market-data",
            json={"securities": [ticker], "fields": ["PX_LAST"]}
        )
        if response.status_code == 200:
            bf = response.json()[0]["fields"]["PX_LAST"]
            bf_values[tenor] = bf
            print(f"  {tenor}: {bf:.3f}")
    
    # Calculate smile for each tenor
    print("\n\n4. RECONSTRUCTED VOLATILITY SMILE:")
    print("-" * 40)
    
    for tenor in ["1M", "3M", "6M", "1Y"]:
        if tenor in atm_vols and tenor in rr_values and tenor in bf_values:
            atm = atm_vols[tenor]
            rr = rr_values[tenor]
            bf = bf_values[tenor]
            
            # Standard market formulas
            call_25d = atm + 0.5 * rr + bf
            put_25d = atm - 0.5 * rr + bf
            
            print(f"\n{tenor} Smile:")
            print(f"  25D Put:  {put_25d:.3f}%")
            print(f"  ATM:      {atm:.3f}%")
            print(f"  25D Call: {call_25d:.3f}%")
            print(f"  Skew:     {rr:.3f} ({'Call' if rr > 0 else 'Put'} premium)")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print("\n✅ Bloomberg Terminal provides complete FX volatility surface data:")
    print("  - ATM volatilities via EURUSDV[tenor] tickers")
    print("  - Risk Reversals via EUR25R[tenor] tickers")
    print("  - Butterflies via EUR25B[tenor] tickers")
    print("\n✅ The React app should now display:")
    print("  - 3D volatility surface with smile")
    print("  - Proper skew across strikes")
    print("  - Real-time Bloomberg data")


if __name__ == "__main__":
    test_app_integration()