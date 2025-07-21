#!/usr/bin/env python3
"""
Bloomberg API Test Script - Checkpoint July 16, 2025
Tests all working endpoints with real Bloomberg data
"""

import requests
import json
from datetime import datetime

# API Configuration
API_URL = "http://20.172.249.92:8080"
API_KEY = "test"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_fx_rates():
    """Test FX rates endpoint"""
    print("\n=== Testing FX Rates Endpoint ===")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "currency_pairs": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF"]
    }
    
    response = requests.post(f"{API_URL}/api/fx/rates/live", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Data count: {result['data']['data_count']}")
        print(f"Sample data:")
        for item in result['data']['raw_data'][:2]:  # Show first 2
            print(f"  {item['currency_pair']}: {item['PX_LAST']} (Bid: {item['PX_BID']}, Ask: {item['PX_ASK']})")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_fx_volatility():
    """Test FX volatility endpoint"""
    print("\n=== Testing FX Volatility Endpoint ===")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test different combinations
    test_cases = [
        {
            "name": "Major pairs - 1M ATM",
            "data": {
                "currency_pairs": ["EURUSD", "GBPUSD", "USDJPY"],
                "tenors": ["1M"],
                "deltas": ["ATM"]
            }
        },
        {
            "name": "EURUSD - Full volatility smile",
            "data": {
                "currency_pairs": ["EURUSD"],
                "tenors": ["1M", "3M"],
                "deltas": ["25D", "10D", "ATM", "10C", "25C"]
            }
        },
        {
            "name": "All tenors - ATM",
            "data": {
                "currency_pairs": ["EURUSD", "GBPUSD"],
                "tenors": ["1W", "1M", "3M", "6M", "1Y"],
                "deltas": ["ATM"]
            }
        }
    ]
    
    all_success = True
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        response = requests.post(f"{API_URL}/api/fx/volatility", json=test['data'], headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Total points: {result['data']['total_points']}")
            print(f"Successful points: {result['data']['successful_points']}")
            print(f"Sample volatilities:")
            for vol in result['data']['volatility_surface'][:3]:  # Show first 3
                print(f"  {vol['ticker']}: {vol['volatility']}%")
        else:
            print(f"Error: {response.text}")
            all_success = False
    
    return all_success

def test_bloomberg_reference():
    """Test generic Bloomberg reference data endpoint"""
    print("\n=== Testing Bloomberg Reference Data Endpoint ===")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test with various securities
    data = {
        "securities": [
            "EURUSD Curncy",
            "GBPUSD Curncy",
            "SPX Index",
            "AAPL US Equity"
        ],
        "fields": ["PX_LAST", "PX_BID", "PX_ASK", "CHG_PCT_1D", "VOLUME"]
    }
    
    response = requests.post(f"{API_URL}/api/bloomberg/reference", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Securities processed:")
        for sec in result['data']['securities_data']:
            if sec['success']:
                print(f"  {sec['security']}: {sec['fields'].get('PX_LAST', 'N/A')}")
            else:
                print(f"  {sec['security']}: ERROR - {sec.get('error', 'Unknown error')}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def main():
    """Run all tests"""
    print(f"Bloomberg API Test Suite")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"API URL: {API_URL}")
    print(f"="*50)
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("FX Rates", test_fx_rates),
        ("FX Volatility", test_fx_volatility),
        ("Bloomberg Reference Data", test_bloomberg_reference)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\nERROR in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{name}: {status}")
    
    total_pass = sum(1 for _, s in results if s)
    print(f"\nTotal: {total_pass}/{len(results)} passed")

if __name__ == "__main__":
    main()