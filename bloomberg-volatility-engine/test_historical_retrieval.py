#!/usr/bin/env python3
"""
Test Bloomberg historical data retrieval capabilities
Determine if we can get historical volatility surface data
"""

import requests
import json
from datetime import datetime, timedelta

def test_historical_capabilities():
    """Test various approaches to get historical data from Bloomberg"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🕰️ TESTING BLOOMBERG HISTORICAL DATA CAPABILITIES")
    print("=" * 60)
    
    # Test 1: Try Bloomberg historical data request format
    print("\n1. TESTING BLOOMBERG HISTORICAL REQUEST:")
    print("-" * 40)
    
    # Generate some historical dates
    dates = []
    for i in range(10, 0, -1):  # Last 10 days
        date = datetime.now() - timedelta(days=i)
        dates.append(date.strftime("%Y%m%d"))
    
    historical_requests = [
        {
            "name": "Historical with BDH request type",
            "endpoint": "/api/historical-data",  # Try dedicated endpoint
            "request": {
                "securities": ["EURUSDV1M Curncy"],
                "fields": ["PX_LAST"],
                "start_date": dates[0],
                "end_date": dates[-1]
            }
        },
        {
            "name": "Market data with date range",
            "endpoint": "/api/market-data",
            "request": {
                "securities": ["EURUSDV1M Curncy", "EUR25R1M Curncy"],
                "fields": ["PX_LAST"],
                "start_date": dates[0],
                "end_date": dates[-1],
                "request_type": "HistoricalDataRequest"
            }
        },
        {
            "name": "Individual date requests",
            "endpoint": "/api/market-data",
            "request": {
                "securities": ["EURUSD Curncy"],
                "fields": ["PX_LAST", "VOLATILITY_30D"],
                "override_date": dates[5]  # Try specific date
            }
        }
    ]
    
    for test in historical_requests:
        print(f"\nTrying: {test['name']}")
        print(f"Endpoint: {test['endpoint']}")
        try:
            response = requests.post(
                f"{base_url}{test['endpoint']}",
                json=test['request'],
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"Error: {response.text[:200]}")
        except Exception as e:
            print(f"Exception: {str(e)}")
    
    # Test 2: Check for time series fields
    print("\n\n2. TESTING TIME SERIES FIELDS:")
    print("-" * 40)
    
    time_series_fields = [
        # Historical close prices
        "PX_CLOSE_1D", "PX_CLOSE_2D", "PX_CLOSE_3D", "PX_CLOSE_4D", "PX_CLOSE_5D",
        "PX_CLOSE_10D", "PX_CLOSE_20D", "PX_CLOSE_30D",
        
        # Historical volatilities
        "VOLATILITY_30D_1D_AGO", "VOLATILITY_30D_5D_AGO", "VOLATILITY_30D_10D_AGO",
        
        # Moving averages
        "MOV_AVG_5D", "MOV_AVG_10D", "MOV_AVG_20D",
        
        # Historical highs/lows
        "HIGH_5D", "LOW_5D", "HIGH_10D", "LOW_10D"
    ]
    
    # Test in batches
    batch_size = 5
    found_historical = {}
    
    for i in range(0, len(time_series_fields), batch_size):
        batch = time_series_fields[i:i+batch_size]
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": ["EURUSD Curncy"], "fields": batch},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()[0]["fields"]
                for field, value in data.items():
                    if value is not None:
                        found_historical[field] = value
                        print(f"  ✓ {field}: {value}")
        except:
            pass
    
    # Test 3: Check available API endpoints
    print("\n\n3. CHECKING API ENDPOINTS:")
    print("-" * 40)
    
    endpoints_to_test = [
        "/api/historical",
        "/api/history",
        "/api/time-series",
        "/api/bdh",  # Bloomberg Data History
        "/api/reference-data"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=2)
            print(f"  {endpoint}: {response.status_code}")
        except:
            print(f"  {endpoint}: Not available")
    
    # Analysis
    print("\n\n" + "=" * 60)
    print("📊 HISTORICAL DATA COLLECTION STRATEGY")
    print("=" * 60)
    
    if found_historical:
        print("\nAVAILABLE HISTORICAL FIELDS:")
        for field, value in found_historical.items():
            print(f"  - {field}: {value}")
    
    print("\nRECOMMENDED APPROACH:")
    print("  1. DAILY SNAPSHOT COLLECTION (Primary Method)")
    print("     - Run collection script daily at fixed time")
    print("     - Store complete volatility surface snapshot")
    print("     - Build historical database over time")
    print("")
    print("  2. USE AVAILABLE LOOKBACK FIELDS")
    print("     - PX_CLOSE_[N]D for historical spot rates")
    print("     - Calculate changes and trends")
    print("")
    print("  3. HISTORICAL SURFACE STORAGE SCHEMA:")
    print("     ```")
    print("     Date | Pair | Tenor | Spot | ATM_Vol | 25D_RR | 25D_BF | 10D_RR | 10D_BF")
    print("     ```")
    print("")
    print("  4. IMPLEMENTATION PLAN:")
    print("     - Set up scheduled task on Bloomberg VM")
    print("     - Collect data every market day at 4PM London")
    print("     - Store in Azure Blob Storage or Synapse")
    print("     - Build analytics layer on historical data")


if __name__ == "__main__":
    test_historical_capabilities()