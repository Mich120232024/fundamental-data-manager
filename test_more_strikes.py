#!/usr/bin/env python3
"""
Test Bloomberg API for additional strikes
"""
import requests
import json

API_BASE = "http://20.172.249.92:8080"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test"
}

# Test different strikes by examining what securities the API tries to request
test_request = {
    "currency_pairs": ["EURUSD"], 
    "tenors": ["1M"]
}

print("Testing your Bloomberg API to see what strikes it requests...")

try:
    response = requests.post(f"{API_BASE}/api/fx/volatility/live", 
                           json=test_request, 
                           headers=headers,
                           timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print("API Response:")
        print(json.dumps(data, indent=2))
        
        # Check what securities were requested
        if 'data' in data and 'raw_data' in data['data']:
            securities = [item.get('security', '') for item in data['data']['raw_data']]
            print("\nSecurities requested:")
            for sec in securities:
                print(f"  - {sec}")
                
            # Analyze what strikes were included
            strikes_found = set()
            for sec in securities:
                if 'RR' in sec or 'BF' in sec:
                    # Extract strike (e.g., "25" from "EURUSD25RR1M")
                    import re
                    match = re.search(r'(\d+)(?:RR|BF)', sec)
                    if match:
                        strikes_found.add(f"{match.group(1)}D")
            
            print(f"\nStrikes currently supported: {sorted(strikes_found)}")
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error testing API: {e}")