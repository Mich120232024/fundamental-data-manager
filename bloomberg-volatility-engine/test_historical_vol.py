#!/usr/bin/env python3
"""
Test historical volatility data availability from Bloomberg
"""

import requests
import json
from datetime import datetime, timedelta
import pandas as pd

def test_historical_volatility():
    """Test historical data retrieval for volatility surfaces"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🕐 HISTORICAL VOLATILITY DATA TEST")
    print("=" * 60)
    
    # Test if we can get historical data
    # Note: This assumes Bloomberg API supports historical requests
    # We'll test with standard fields first
    
    print("\n1. TESTING HISTORICAL DATA FIELDS:")
    print("-" * 40)
    
    # Try different approaches to get historical data
    test_requests = [
        {
            "name": "Historical volatility fields",
            "request": {
                "securities": ["EURUSD Curncy"],
                "fields": ["VOLATILITY_30D", "VOLATILITY_90D", "PX_LAST"],
                "start_date": "20250101",  # Try Bloomberg date format
                "end_date": "20250711"
            }
        },
        {
            "name": "Option vol tickers with dates",
            "request": {
                "securities": ["EURUSDV1M Curncy", "EURUSDV3M Curncy"],
                "fields": ["PX_LAST", "PX_MID"],
                "historical": True
            }
        },
        {
            "name": "Historical price fields",
            "request": {
                "securities": ["EURUSD Curncy"],
                "fields": ["PX_LAST", "PX_CLOSE_1D", "PX_CLOSE_2D", "PX_CLOSE_5D"]
            }
        }
    ]
    
    for test in test_requests:
        print(f"\nTesting: {test['name']}")
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json=test['request'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Response: {json.dumps(data, indent=2)}")
            else:
                print(f"  ✗ Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")
    
    # Test specific historical volatility fields
    print("\n\n2. TESTING VOLATILITY HISTORY FIELDS:")
    print("-" * 40)
    
    vol_history_fields = [
        # Try various historical volatility field formats
        "VOLATILITY_30D_HIST",
        "HIST_VOLATILITY_30D",
        "HV30",
        "VOLATILITY_30D_1M_AGO",
        "1M_AGO_VOLATILITY_30D",
        
        # Realized volatility
        "REALIZED_VOL_30D",
        "HISTORICAL_VOL_30D",
        
        # Vol of vol
        "VOL_OF_VOL_30D",
        "VOLATILITY_OF_VOLATILITY"
    ]
    
    batch_size = 5
    for i in range(0, len(vol_history_fields), batch_size):
        batch = vol_history_fields[i:i+batch_size]
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": ["EURUSD Curncy"], "fields": batch},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                for field, value in data['fields'].items():
                    if value is not None:
                        print(f"  ✓ Found: {field} = {value}")
        except:
            pass
    
    # Test if we can get time series data
    print("\n\n3. TESTING TIME SERIES APPROACH:")
    print("-" * 40)
    
    # Generate dates for the last 30 days
    dates = []
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        dates.append(date.strftime("%Y%m%d"))
    
    print(f"Testing retrieval for {len(dates)} historical dates...")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 HISTORICAL DATA ANALYSIS")
    print("=" * 60)
    
    print("\nFOR VOLATILITY SURFACE RECONSTRUCTION:")
    print("  1. Need daily snapshots of ATM vols (1W to 1Y tenors)")
    print("  2. Need daily risk reversals and butterflies")
    print("  3. Need spot rates and forward points")
    print("  4. Store data in time series format")
    
    print("\nSUGGESTED DATA STRUCTURE:")
    print("  - Date | Tenor | ATM_Vol | 25D_RR | 25D_BF | 10D_RR | Spot | Forward")
    print("  - Store in Delta Lake or similar for efficient querying")
    
    print("\nDATA COLLECTION STRATEGY:")
    print("  1. Run daily snapshot collection (via scheduled task)")
    print("  2. Store raw data with timestamps")
    print("  3. Build interpolation functions for surface construction")
    print("  4. Implement volatility smile calibration")


if __name__ == "__main__":
    test_historical_volatility()