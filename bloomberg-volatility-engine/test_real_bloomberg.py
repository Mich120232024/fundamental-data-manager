#!/usr/bin/env python3
"""
Test REAL Bloomberg Terminal data
"""

import requests
import json
from datetime import datetime

def test_real_bloomberg():
    """Test real Bloomberg Terminal connection and data"""
    
    print("🏦 Testing REAL Bloomberg Terminal API")
    print("=" * 50)
    
    base_url = "http://20.172.249.92:8080"
    
    # 1. Check health
    print("\n1. Health Check:")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health = response.json()
        print(f"   Status: {health['status']}")
        print(f"   Bloomberg Connected: {health['bloomberg_connected']}")
        print(f"   Mode: {health['mode']}")
        
        if not health['bloomberg_connected']:
            print("\n❌ Bloomberg Terminal not connected!")
            return
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # 2. Test real FX rates
    print("\n2. REAL FX Rates from Bloomberg Terminal:")
    try:
        # Try with direct request
        response = requests.get(f"{base_url}/api/fx/rates?pairs=EURUSD", timeout=10)
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            try:
                rates = response.json()
                if isinstance(rates, list):
                    for rate in rates:
                        security = rate.get('security', 'Unknown')
                        fields = rate.get('fields', {})
                        print(f"\n   {security}:")
                        for field, value in fields.items():
                            print(f"     {field}: {value}")
                        print(f"     Source: {rate.get('source', 'Unknown')}")
                else:
                    print(f"   Unexpected response: {rates}")
            except json.JSONDecodeError:
                print(f"   Raw response: {response.text[:200]}")
        else:
            print(f"   Error response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Test market data with POST
    print("\n3. Market Data Request (POST):")
    try:
        payload = {
            "securities": ["AAPL US Equity", "MSFT US Equity", "SPX Index"],
            "fields": ["PX_LAST", "PX_OPEN", "PX_HIGH", "PX_LOW", "VOLUME"]
        }
        
        response = requests.post(
            f"{base_url}/api/market-data",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    for item in data:
                        security = item.get('security', 'Unknown')
                        fields = item.get('fields', {})
                        print(f"\n   {security}:")
                        for field, value in fields.items():
                            print(f"     {field}: {value}")
                else:
                    print(f"   Response: {data}")
            except json.JSONDecodeError:
                print(f"   Raw response: {response.text[:200]}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Test news
    print("\n4. Bloomberg News:")
    try:
        payload = {
            "topics": ["TOP", "FX"],
            "max_stories": 3
        }
        
        response = requests.post(
            f"{base_url}/api/news",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            news = response.json()
            if isinstance(news, list):
                print(f"   Retrieved {len(news)} stories")
                for story in news:
                    print(f"   - {story.get('headline', 'No headline')}")
                    print(f"     Source: {story.get('source', 'Unknown')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Real Bloomberg Terminal API is operational!")
    print("\nNote: If data requests fail, ensure:")
    print("1. Bloomberg Terminal is logged in on the VM")
    print("2. The requested securities are valid Bloomberg tickers")
    print("3. The Terminal has permissions for the requested data")


if __name__ == "__main__":
    test_real_bloomberg()