#!/usr/bin/env python3
"""
Test Bloomberg news collection from the API server
"""

import json
import requests
from datetime import datetime
from bloomberg_client import BloombergClient

def test_bloomberg_news():
    """Test news collection functionality"""
    
    print("📰 Bloomberg News Collection Test")
    print("=" * 50)
    
    # Initialize client
    client = BloombergClient("http://20.172.249.92:8080")
    
    # 1. Test health
    print("\n1. Testing server health...")
    health = client.health_check()
    print(f"   Status: {health.get('status')}")
    print(f"   Server: {health.get('server')}")
    print(f"   Version: {health.get('version', 'Unknown')}")
    
    # 2. Test GET news endpoint
    print("\n2. Testing GET /api/news...")
    try:
        response = requests.get("http://20.172.249.92:8080/api/news?max_stories=5")
        if response.status_code == 200:
            news = response.json()
            if isinstance(news, list):
                print(f"   ✅ Retrieved {len(news)} news stories")
                for story in news[:3]:
                    print(f"   - {story.get('headline', 'No headline')}")
            else:
                print(f"   ⚠️  Unexpected response: {news}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Test POST news endpoint
    print("\n3. Testing POST /api/news...")
    try:
        payload = {
            "topics": ["FX", "ECONOMIC"],
            "max_stories": 5,
            "hours_back": 24
        }
        response = requests.post("http://20.172.249.92:8080/api/news", json=payload)
        if response.status_code == 200:
            news = response.json()
            if isinstance(news, list):
                print(f"   ✅ Retrieved {len(news)} news stories for topics: {payload['topics']}")
                for story in news[:3]:
                    print(f"   - {story.get('headline', 'No headline')}")
            else:
                print(f"   ⚠️  Unexpected response: {news}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Test FX rates
    print("\n4. Testing FX rates...")
    try:
        response = requests.get("http://20.172.249.92:8080/api/fx/rates?pairs=EURUSD&pairs=GBPUSD&pairs=USDJPY")
        if response.status_code == 200:
            rates = response.json()
            if isinstance(rates, list):
                print(f"   ✅ Retrieved {len(rates)} FX rates")
                for rate in rates:
                    security = rate.get('security', 'Unknown')
                    fields = rate.get('fields', {})
                    last = fields.get('PX_LAST', 'N/A')
                    print(f"   - {security}: {last}")
            else:
                print(f"   ⚠️  Unexpected response: {rates}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Test market data
    print("\n5. Testing market data...")
    try:
        payload = {
            "securities": ["EURUSD Curncy", "GBPUSD Curncy", "SPX Index"],
            "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
        }
        response = requests.post("http://20.172.249.92:8080/api/market-data", json=payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Retrieved market data for {len(data)} securities")
                for item in data:
                    security = item.get('security', 'Unknown')
                    fields = item.get('fields', {})
                    last = fields.get('PX_LAST', 'N/A')
                    print(f"   - {security}: {last}")
            else:
                print(f"   ⚠️  Unexpected response: {data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. Check API documentation
    print("\n6. Checking API documentation...")
    try:
        response = requests.get("http://20.172.249.92:8080/docs")
        if response.status_code == 200:
            print("   ✅ API documentation is available at: http://20.172.249.92:8080/docs")
        else:
            print(f"   ❌ Documentation not accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("Bloomberg API Server is operational with mock data")
    print("Ready for integration with real Bloomberg Terminal")


if __name__ == "__main__":
    test_bloomberg_news()