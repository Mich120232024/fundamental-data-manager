#!/usr/bin/env python3
"""
Test EURUSD Risk Reversal and Butterfly extraction
Focus on one currency pair to get the correct fields
"""

import requests
import json
from datetime import datetime

def test_eurusd_volatility_fields():
    """Test specific volatility fields for EURUSD"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 EURUSD VOLATILITY FIELD TESTING")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # According to yesterday's logs, these fields were found:
    # "25D_RR_1M", "25D_RR_3M", "25D_RR_6M", "25D_RR_1Y"
    # "25D_BF_1M", "25D_BF_3M", "25D_BF_6M"
    
    # Test 1: ATM volatilities using correct ticker format
    print("\n1. TESTING ATM VOLATILITIES (Verified Working):")
    print("-" * 40)
    
    atm_tickers = [
        "EURUSDV1M Curncy",  # 1-month ATM vol
        "EURUSDV3M Curncy",  # 3-month ATM vol  
        "EURUSDV6M Curncy",  # 6-month ATM vol
        "EURUSDV1Y Curncy",  # 1-year ATM vol
    ]
    
    for ticker in atm_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                value = data['fields'].get('PX_LAST')
                if value:
                    print(f"  ✓ {ticker}: {value}% (ATM volatility)")
        except Exception as e:
            print(f"  ✗ {ticker}: Error - {e}")
    
    # Test 2: Risk Reversals and Butterflies as fields on base ticker
    print("\n\n2. TESTING RISK REVERSALS & BUTTERFLIES (as fields):")
    print("-" * 40)
    
    smile_fields = [
        # Risk Reversals - exactly as found yesterday
        "25D_RR_1M", "25D_RR_3M", "25D_RR_6M", "25D_RR_1Y",
        
        # Butterflies - exactly as found yesterday
        "25D_BF_1M", "25D_BF_3M", "25D_BF_6M", "25D_BF_1Y",
        
        # Try 10 delta as well
        "10D_RR_1M", "10D_RR_3M", "10D_RR_6M", "10D_RR_1Y",
        "10D_BF_1M", "10D_BF_3M", "10D_BF_6M", "10D_BF_1Y"
    ]
    
    # Test on EURUSD base ticker
    try:
        response = requests.post(
            f"{base_url}/api/market-data",
            json={"securities": ["EURUSD Curncy"], "fields": smile_fields},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            print(f"\nResults for EURUSD Curncy:")
            found_count = 0
            for field, value in data['fields'].items():
                if value is not None:
                    print(f"  ✓ {field}: {value}")
                    found_count += 1
                else:
                    print(f"  ✗ {field}: null")
            print(f"\nFound {found_count} non-null fields out of {len(smile_fields)}")
    except Exception as e:
        print(f"Error testing fields: {e}")
    
    # Test 3: Try option-specific tickers for RR/BF
    print("\n\n3. TESTING OPTION-SPECIFIC TICKERS:")
    print("-" * 40)
    
    option_tickers = [
        # Risk Reversal tickers
        "EUR25DR1M Curncy",  # 1M 25-delta risk reversal
        "EUR25DR3M Curncy",  # 3M 25-delta risk reversal
        "EUR25DR6M Curncy",  # 6M 25-delta risk reversal
        "EUR25DR1Y Curncy",  # 1Y 25-delta risk reversal
        
        # Butterfly tickers
        "EUR25BF1M Curncy",  # 1M 25-delta butterfly
        "EUR25BF3M Curncy",  # 3M 25-delta butterfly
        "EUR25BF6M Curncy",  # 6M 25-delta butterfly
        
        # Alternative formats
        "EURUSD25RR1M Curncy",
        "EURUSD25BF1M Curncy",
    ]
    
    for ticker in option_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID"]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                fields = data.get('fields', {})
                if any(fields.values()):
                    print(f"  ✓ {ticker}: {fields}")
        except Exception as e:
            pass
    
    # Test 4: Historical data request
    print("\n\n4. TESTING HISTORICAL DATA REQUEST:")
    print("-" * 40)
    
    try:
        # Request historical data for ATM vol
        response = requests.post(
            f"{base_url}/api/historical-data",
            json={
                "security": "EURUSDV1M Curncy",
                "fields": ["PX_LAST"],
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                print(f"  ✓ Historical data available: {len(data['data'])} points")
                print(f"    Sample: {data['data'][0] if data['data'] else 'No data'}")
        else:
            print(f"  ✗ Historical request failed: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 SUMMARY & RECOMMENDATIONS")
    print("=" * 60)
    print("\n1. ATM volatilities are available via tickers like EURUSDV1M Curncy")
    print("2. Risk Reversals and Butterflies need to be tested as fields on base ticker")
    print("3. If RR/BF fields don't work, may need to calculate from individual strikes")
    print("4. Historical data API is available for backtesting")
    
    print("\n💡 NEXT STEPS:")
    print("1. If RR/BF fields return null, try getting individual 25D call/put vols")
    print("2. Calculate RR = vol(25D Call) - vol(25D Put)")
    print("3. Calculate BF = 0.5*[vol(25D Call) + vol(25D Put)] - vol(ATM)")


if __name__ == "__main__":
    test_eurusd_volatility_fields()