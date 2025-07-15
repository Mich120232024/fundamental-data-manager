#!/usr/bin/env python3
"""
Test the exact Bloomberg tickers used in production
Based on fx_vol_surface_collector.py
"""

import requests
import json
from datetime import datetime

def test_production_tickers():
    """Test the production ticker format for RR and BF"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 TESTING PRODUCTION BLOOMBERG TICKERS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print("Based on production fx_vol_surface_collector.py")
    print("=" * 60)
    
    # Test Risk Reversal tickers (format: EUR25R1M Curncy)
    print("\n1. RISK REVERSAL TICKERS:")
    print("-" * 40)
    
    rr_tickers = [
        "EUR25R1M Curncy",  # EURUSD 25-delta 1-month RR
        "EUR25R3M Curncy",  # EURUSD 25-delta 3-month RR
        "EUR25R6M Curncy",  # EURUSD 25-delta 6-month RR
        "EUR25R1Y Curncy",  # EURUSD 25-delta 1-year RR
        "EUR10R1M Curncy",  # EURUSD 10-delta 1-month RR
        "EUR10R3M Curncy",  # EURUSD 10-delta 3-month RR
    ]
    
    found_rr = False
    for ticker in rr_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID", "PX_BID", "PX_ASK"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                fields = data.get('fields', {})
                if any(v is not None for v in fields.values()):
                    print(f"  ✓ {ticker}: {fields}")
                    found_rr = True
                else:
                    print(f"  ✗ {ticker}: No data")
        except Exception as e:
            print(f"  ✗ {ticker}: Error - {e}")
    
    # Test Butterfly tickers (format: EUR25B1M Curncy)
    print("\n\n2. BUTTERFLY TICKERS:")
    print("-" * 40)
    
    bf_tickers = [
        "EUR25B1M Curncy",  # EURUSD 25-delta 1-month BF
        "EUR25B3M Curncy",  # EURUSD 25-delta 3-month BF
        "EUR25B6M Curncy",  # EURUSD 25-delta 6-month BF
        "EUR25B1Y Curncy",  # EURUSD 25-delta 1-year BF
        "EUR10B1M Curncy",  # EURUSD 10-delta 1-month BF
        "EUR10B3M Curncy",  # EURUSD 10-delta 3-month BF
    ]
    
    found_bf = False
    for ticker in bf_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID", "PX_BID", "PX_ASK"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                fields = data.get('fields', {})
                if any(v is not None for v in fields.values()):
                    print(f"  ✓ {ticker}: {fields}")
                    found_bf = True
                else:
                    print(f"  ✗ {ticker}: No data")
        except Exception as e:
            print(f"  ✗ {ticker}: Error - {e}")
    
    # Test alternative ticker formats
    print("\n\n3. ALTERNATIVE TICKER FORMATS:")
    print("-" * 40)
    
    alt_tickers = [
        "EURUSD25R1M Curncy",   # Full pair code
        "EUR/USD25R1M Curncy",  # With slash
        "EUR 25R 1M Curncy",    # With spaces
        "EUR25RR1M Curncy",     # Double R
        "EURRR251M Curncy",     # Different order
    ]
    
    for ticker in alt_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST"]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                value = data.get('fields', {}).get('PX_LAST')
                if value is not None:
                    print(f"  ✓ {ticker}: {value}")
        except:
            pass
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    if found_rr or found_bf:
        print("\n✅ PRODUCTION TICKERS ARE WORKING!")
        print("The Bloomberg Terminal has FX option volatility data")
        print("Update the React app to use these tickers")
    else:
        print("\n❌ PRODUCTION TICKERS NOT RETURNING DATA")
        print("\nPossible reasons:")
        print("1. Bloomberg Terminal subscription has changed")
        print("2. These tickers require specific Terminal configuration")
        print("3. Data is only available during market hours")
        print("4. Need to use Bloomberg Excel Add-in or OVDV screen")
        
        print("\n💡 NEXT STEPS:")
        print("1. Check Bloomberg Terminal directly for these tickers")
        print("2. Verify subscription includes FX option volatility data")
        print("3. Contact Bloomberg support about API access")
        print("4. Consider using Excel Add-in with BDP/BDH functions")


if __name__ == "__main__":
    test_production_tickers()