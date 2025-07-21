#!/usr/bin/env python3
"""
Debug ATM response
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import requests
import json

def debug_atm():
    """Debug ATM data"""
    
    base_url = "http://20.172.249.92:8080"
    api_key = "test"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Just test ATM
    securities = ["EURUSDV1M BGN Curncy"]
    
    payload = {
        "securities": securities,
        "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
    }
    
    print("Testing ATM security:")
    response = requests.post(
        f"{base_url}/api/bloomberg/reference",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        
        # Check securities_data
        if data.get('data', {}).get('securities_data'):
            for sec_data in data['data']['securities_data']:
                print(f"\nSecurity: {sec_data['security']}")
                print(f"Success: {sec_data['success']}")
                if sec_data['success']:
                    print(f"Fields: {sec_data['fields']}")


if __name__ == "__main__":
    debug_atm()