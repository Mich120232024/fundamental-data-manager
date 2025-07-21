#!/usr/bin/env python3
"""
Test EURUSD Volatility Data - Simple Table Display
Bloomberg API Integration - ZERO MOCK DATA
"""
import requests
import json
from datetime import datetime

# Bloomberg API Configuration
API_BASE = "http://20.172.249.92:8080"
API_TOKEN = "test"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

def test_volatility_api():
    """Test the volatility API and display results in table format"""
    
    print("🔴 BLOOMBERG VOLATILITY DATA TEST")
    print("=" * 60)
    
    # Test request for EURUSD volatility
    test_request = {
        "currency_pairs": ["EURUSD"], 
        "tenors": ["1W", "1M", "3M", "6M", "1Y"]
    }
    
    print(f"📡 Requesting EURUSD volatility data...")
    print(f"🎯 Tenors: {', '.join(test_request['tenors'])}")
    print(f"🌍 API: {API_BASE}/api/fx/volatility/live")
    print("-" * 60)
    
    try:
        # Make API request
        response = requests.post(
            f"{API_BASE}/api/fx/volatility/live",
            json=test_request,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response Success!")
            print(f"📊 Data Source: {data['data']['source']}")
            print(f"⏰ Timestamp: {data['data']['timestamp']}")
            print(f"📈 Total Data Points: {data['data']['data_count']}")
            print("=" * 60)
            
            # Display raw data in table format
            if 'raw_data' in data['data']:
                print("📋 EURUSD VOLATILITY TABLE")
                print("=" * 80)
                print(f"{'Security':<25} {'Last':<10} {'Bid':<10} {'Ask':<10} {'Update Time':<20}")
                print("-" * 80)
                
                for item in data['data']['raw_data']:
                    security = item.get('security', 'N/A')
                    last = item.get('PX_LAST', 'N/A')
                    bid = item.get('PX_BID', 'N/A')
                    ask = item.get('PX_ASK', 'N/A')
                    update_time = item.get('LAST_UPDATE_TIME', 'N/A')
                    
                    print(f"{security:<25} {last:<10} {bid:<10} {ask:<10} {update_time:<20}")
                
                print("=" * 80)
                
                # Analyze strikes found
                strikes_found = set()
                for item in data['data']['raw_data']:
                    security = item.get('security', '')
                    if 'RR' in security or 'BF' in security:
                        # Extract strike (e.g., "25" from "EURUSD25RR1M")
                        import re
                        match = re.search(r'(\d+)(?:RR|BF)', security)
                        if match:
                            strikes_found.add(f"{match.group(1)}D")
                
                print(f"🎯 Strikes Available: {sorted(strikes_found)}")
                print(f"📊 Total Securities: {len(data['data']['raw_data'])}")
                
            else:
                print("⚠️  No raw_data found in response")
                print("Full response structure:")
                print(json.dumps(data, indent=2))
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🔥 Connection Error: {e}")
    except Exception as e:
        print(f"🔥 Unexpected Error: {e}")

def test_spot_rate():
    """Get EURUSD spot rate for reference"""
    print("\n🔴 EURUSD SPOT RATE")
    print("=" * 40)
    
    try:
        response = requests.post(
            f"{API_BASE}/api/fx/rates/live",
            json={"currency_pairs": ["EURUSD"]},
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            spot_data = data['data']['raw_data'][0]
            print(f"💰 EURUSD Spot: {spot_data['PX_LAST']}")
            print(f"📊 Bid/Ask: {spot_data['PX_BID']}/{spot_data['PX_ASK']}")
        else:
            print(f"❌ Spot rate error: {response.status_code}")
            
    except Exception as e:
        print(f"🔥 Spot rate error: {e}")

if __name__ == "__main__":
    # Test spot rate first
    test_spot_rate()
    
    # Test volatility data
    test_volatility_api()
    
    print(f"\n⏰ Test completed at: {datetime.now()}")