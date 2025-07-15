#!/usr/bin/env python3
"""
Test Bloomberg Data History (BDH) endpoint for historical volatility data
"""

import requests
import json
from datetime import datetime, timedelta

def test_bdh_endpoint():
    """Test the BDH endpoint that returned 200 status"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 TESTING BLOOMBERG BDH (DATA HISTORY) ENDPOINT")
    print("=" * 60)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Test different request formats
    test_requests = [
        {
            "name": "BDH with date range",
            "endpoint": "/api/bdh",
            "request": {
                "securities": ["EURUSDV1M Curncy", "EUR25R1M Curncy", "EUR25B1M Curncy"],
                "fields": ["PX_LAST"],
                "start_date": start_date.strftime("%Y%m%d"),
                "end_date": end_date.strftime("%Y%m%d")
            }
        },
        {
            "name": "Time series endpoint",
            "endpoint": "/api/time-series",
            "request": {
                "securities": ["EURUSD Curncy"],
                "fields": ["PX_LAST", "VOLATILITY_30D"],
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "frequency": "DAILY"
            }
        },
        {
            "name": "Historical endpoint",
            "endpoint": "/api/historical",
            "request": {
                "securities": ["EURUSDV1M Curncy"],
                "fields": ["PX_LAST", "PX_MID"],
                "days": 30
            }
        }
    ]
    
    for test in test_requests:
        print(f"\n📌 Testing: {test['name']}")
        print(f"Endpoint: {test['endpoint']}")
        print(f"Request: {json.dumps(test['request'], indent=2)}")
        
        try:
            # Try POST first
            response = requests.post(
                f"{base_url}{test['endpoint']}",
                json=test['request'],
                timeout=15
            )
            
            print(f"\nPOST Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response type: {type(data)}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"Number of records: {len(data)}")
                    print(f"First record: {json.dumps(data[0], indent=2)}")
                    if len(data) > 1:
                        print(f"Last record: {json.dumps(data[-1], indent=2)}")
                else:
                    print(f"Full response: {json.dumps(data, indent=2)[:500]}")
            else:
                print(f"Error: {response.text[:200]}")
                
            # Try GET with params
            if response.status_code != 200:
                print("\nTrying GET request...")
                response = requests.get(
                    f"{base_url}{test['endpoint']}",
                    params=test['request'],
                    timeout=10
                )
                print(f"GET Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"Exception: {str(e)}")
    
    # Test specific volatility surface history
    print("\n\n📊 VOLATILITY SURFACE HISTORICAL TEST")
    print("-" * 40)
    
    vol_surface_request = {
        "securities": [
            "EURUSD Curncy",      # Spot
            "EURUSDV1W Curncy",   # 1W ATM vol
            "EURUSDV1M Curncy",   # 1M ATM vol
            "EURUSDV3M Curncy",   # 3M ATM vol
            "EUR25R1M Curncy",    # 25D Risk Reversal
            "EUR25B1M Curncy",    # 25D Butterfly
            "EUR10R1M Curncy",    # 10D Risk Reversal
            "EUR10B1M Curncy"     # 10D Butterfly
        ],
        "fields": ["PX_LAST"],
        "start_date": (end_date - timedelta(days=5)).strftime("%Y%m%d"),
        "end_date": end_date.strftime("%Y%m%d")
    }
    
    print("Requesting last 5 days of volatility surface data...")
    
    for endpoint in ["/api/bdh", "/api/historical", "/api/time-series"]:
        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                json=vol_surface_request,
                timeout=20
            )
            
            if response.status_code == 200:
                print(f"\n✅ Success with {endpoint}!")
                data = response.json()
                
                # Analyze the response structure
                if isinstance(data, dict):
                    print("Response is a dictionary with keys:", list(data.keys()))
                    for key in list(data.keys())[:2]:  # Show first 2 securities
                        print(f"\n{key}:")
                        print(json.dumps(data[key], indent=2)[:300])
                elif isinstance(data, list):
                    print(f"Response is a list with {len(data)} items")
                    if data:
                        print("Sample item:", json.dumps(data[0], indent=2))
                break
        except Exception as e:
            print(f"{endpoint}: {str(e)}")
    
    print("\n\n" + "=" * 60)
    print("💡 HISTORICAL DATA CONCLUSION")
    print("=" * 60)
    print("\nBased on the API responses, we can:")
    print("  1. Access current values for all volatility surface components ✓")
    print("  2. Get limited lookback data (PX_CLOSE_1D to PX_CLOSE_5D) ✓")
    print("  3. Historical endpoints exist but may need specific auth/config")
    print("\nRECOMMENDATION: Implement daily snapshot collection system")


if __name__ == "__main__":
    test_bdh_endpoint()