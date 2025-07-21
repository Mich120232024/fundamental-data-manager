#!/usr/bin/env python3
"""
Debug full processing with all securities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import requests
import json

def debug_full_processing():
    """Debug full processing"""
    
    base_url = "http://20.172.249.92:8080"
    api_key = "test"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    currency_pair = "EURUSD"
    tenor = "1M"
    
    # Build securities
    securities = []
    securities.append(f"{currency_pair}V{tenor} BGN Curncy")
    
    for delta in ["5", "10", "15", "25", "35"]:
        securities.append(f"{currency_pair}{delta}R{tenor} BGN Curncy")
        securities.append(f"{currency_pair}{delta}B{tenor} BGN Curncy")
    
    payload = {
        "securities": securities,
        "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
    }
    
    print(f"Requesting {len(securities)} securities...")
    response = requests.post(
        f"{base_url}/api/bloomberg/reference",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Process each security
        print("\nProcessing securities:")
        for i, sec_data in enumerate(data['data']['securities_data']):
            security = sec_data['security']
            success = sec_data['success']
            
            print(f"\n{i}. {security}")
            print(f"   Success: {success}")
            
            if success:
                fields_data = sec_data['fields']
                
                # Parse security
                if "V" in security and "R" not in security and "B" not in security:
                    product = "ATM"
                    delta = "ATM"
                elif "R" in security:
                    product = "RR"
                    delta = security.split(currency_pair)[1].split("R")[0] + "D"
                elif "B" in security:
                    product = "BF"
                    delta = security.split(currency_pair)[1].split("B")[0] + "D"
                else:
                    product = "UNKNOWN"
                    delta = "UNKNOWN"
                
                print(f"   Product: {product}, Delta: {delta}")
                print(f"   PX_LAST: {fields_data.get('PX_LAST')}")


if __name__ == "__main__":
    debug_full_processing()