#!/usr/bin/env python3
"""
Test Bloomberg API Server Connection
Run this from your local machine to test the Bloomberg API server on the VM
"""

import json
import requests
from datetime import datetime
from bloomberg_client import BloombergClient

def test_bloomberg_api():
    """Test Bloomberg API server connection and functionality"""
    
    # Bloomberg VM connection details
    # Using the public IP since we're connecting from outside the VNet
    BLOOMBERG_SERVER = "http://20.172.249.92:8080"
    
    print("Bloomberg API Server Test")
    print("=" * 60)
    print(f"Server: {BLOOMBERG_SERVER}")
    print(f"Time: {datetime.now()}")
    print()
    
    # Initialize client
    client = BloombergClient(server_url=BLOOMBERG_SERVER)
    
    # Test 1: Health Check
    print("1. Testing server health...")
    try:
        health = client.health_check()
        print(f"   ✓ Server Status: {health.get('status', 'unknown')}")
        print(f"   ✓ Bloomberg Connected: {health.get('bloomberg_connected', False)}")
        print(f"   ✓ Server Time: {health.get('timestamp', 'N/A')}")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        return
    
    # Test 2: Get Latest News
    print("\n2. Testing news retrieval...")
    try:
        news = client.get_news(
            topics=["FX", "ECONOMIC"],
            max_stories=5,
            hours_back=24
        )
        print(f"   ✓ Retrieved {len(news)} news stories")
        
        # Display sample headlines
        if news:
            print("\n   Recent Headlines:")
            for i, story in enumerate(news[:3], 1):
                print(f"   {i}. {story['datetime']}: {story['headline']}")
                
    except Exception as e:
        print(f"   ✗ News retrieval failed: {e}")
    
    # Test 3: Get FX Rates
    print("\n3. Testing FX rates...")
    try:
        rates = client.get_fx_rates(["EURUSD", "GBPUSD", "USDJPY"])
        print(f"   ✓ Retrieved {len(rates)} FX rates")
        
        # Display rates
        if rates:
            print("\n   Current FX Rates:")
            for rate in rates:
                security = rate['security']
                fields = rate.get('fields', {})
                last_price = fields.get('PX_LAST', 'N/A')
                print(f"   - {security}: {last_price}")
                
    except Exception as e:
        print(f"   ✗ FX rates failed: {e}")
    
    # Test 4: Search News
    print("\n4. Testing news search...")
    try:
        search_results = client.search_news(
            query="Federal Reserve",
            max_results=3,
            days_back=7
        )
        
        count = search_results.get('count', 0)
        print(f"   ✓ Found {count} stories matching 'Federal Reserve'")
        
        if search_results.get('results'):
            print("\n   Search Results:")
            for i, story in enumerate(search_results['results'][:3], 1):
                print(f"   {i}. {story['headline']}")
                
    except Exception as e:
        print(f"   ✗ News search failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")


def test_direct_api_calls():
    """Test direct API calls without client library"""
    
    BLOOMBERG_SERVER = "http://20.172.249.92:8080"
    
    print("\nDirect API Call Tests")
    print("=" * 60)
    
    # Direct health check
    print("\n1. Direct health check...")
    try:
        response = requests.get(f"{BLOOMBERG_SERVER}/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✓ Status Code: {response.status_code}")
            print(f"   ✓ Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   ✗ Status Code: {response.status_code}")
            print(f"   ✗ Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("   ✗ Connection failed - Server may not be running")
        print("   - Check if Bloomberg API server is running on the VM")
        print("   - Check if port 8080 is open in the NSG")
        print("   - Check if Windows Firewall allows port 8080")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Direct news API call
    print("\n2. Direct news API call...")
    try:
        payload = {
            "topics": ["TOP"],
            "max_stories": 3,
            "hours_back": 12
        }
        response = requests.post(
            f"{BLOOMBERG_SERVER}/api/news", 
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            print(f"   ✓ Status Code: {response.status_code}")
            news = response.json()
            print(f"   ✓ Retrieved {len(news)} stories")
        else:
            print(f"   ✗ Status Code: {response.status_code}")
            print(f"   ✗ Response: {response.text}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")


if __name__ == "__main__":
    # First test with client library
    test_bloomberg_api()
    
    # Then test direct API calls
    test_direct_api_calls()
    
    print("\n📝 Notes:")
    print("- If connection fails, ensure:")
    print("  1. Bloomberg API server is running on the VM")
    print("  2. NSG allows port 8080 from your IP")
    print("  3. Windows Firewall on VM allows port 8080")
    print("  4. Bloomberg Terminal is running and logged in")