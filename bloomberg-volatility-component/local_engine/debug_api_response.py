#!/usr/bin/env python3
"""
Debug API response to understand data structure
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import requests
import json

def debug_api_response():
    """Debug the API response"""
    
    base_url = "http://20.172.249.92:8080"
    api_key = "test"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Build securities list
    securities = []
    currency_pair = "EURUSD"
    tenor = "1M"
    
    # ATM
    securities.append(f"{currency_pair}V{tenor} BGN Curncy")
    
    # Risk Reversals and Butterflies for all deltas
    for delta in ["5D", "10D", "15D", "20D", "25D", "30D", "35D", "40D", "45D"]:
        securities.append(f"{currency_pair}{delta}R{tenor} BGN Curncy")
        securities.append(f"{currency_pair}{delta}B{tenor} BGN Curncy")
    
    print(f"Requesting {len(securities)} securities...")
    print("\nFirst few securities:")
    for sec in securities[:5]:
        print(f"  - {sec}")
    
    # Make request
    payload = {
        "securities": securities,
        "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
    }
    
    response = requests.post(
        f"{base_url}/api/bloomberg/reference",
        json=payload,
        headers=headers
    )
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse success: {data.get('success')}")
        
        if data.get('data'):
            securities_data = data['data'].get('securities_data', [])
            print(f"\nNumber of securities in response: {len(securities_data)}")
            
            # Show first few responses
            print("\nFirst few responses:")
            for i, sec_data in enumerate(securities_data[:5]):
                print(f"\nSecurity {i+1}:")
                print(f"  Security: {sec_data.get('security')}")
                print(f"  Success: {sec_data.get('success')}")
                if sec_data.get('success'):
                    fields = sec_data.get('fields', {})
                    print(f"  PX_LAST: {fields.get('PX_LAST')}")
                    print(f"  PX_BID: {fields.get('PX_BID')}")
                    print(f"  PX_ASK: {fields.get('PX_ASK')}")
                else:
                    print(f"  Error: {sec_data.get('error')}")
            
            # Count successful vs failed
            successful = sum(1 for s in securities_data if s.get('success'))
            failed = sum(1 for s in securities_data if not s.get('success'))
            print(f"\nSummary:")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            
            # Show all failed securities
            if failed > 0:
                print("\nFailed securities:")
                for sec_data in securities_data:
                    if not sec_data.get('success'):
                        print(f"  - {sec_data.get('security')}: {sec_data.get('error')}")
        else:
            print("\nNo data in response")
            print(f"Full response: {json.dumps(data, indent=2)}")
    else:
        print(f"\nError response: {response.text}")


if __name__ == "__main__":
    debug_api_response()