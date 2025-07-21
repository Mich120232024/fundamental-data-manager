#!/usr/bin/env python3
"""
Test with correct ticker formats (no D in delta)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import requests
import json

def test_correct_tickers():
    """Test with correct ticker formats"""
    
    base_url = "http://20.172.249.92:8080"
    api_key = "test"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Test known working tickers first
    print("Testing known working tickers...")
    known_working = [
        "EURUSDV1M BGN Curncy",      # ATM
        "EURUSD25R1M BGN Curncy",     # 25D Risk Reversal
        "EURUSD25B1M BGN Curncy",     # 25D Butterfly
        "EURUSD10B1M BGN Curncy",     # 10D Butterfly
    ]
    
    payload = {
        "securities": known_working,
        "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
    }
    
    response = requests.post(
        f"{base_url}/api/bloomberg/reference",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        for sec_data in data['data']['securities_data']:
            print(f"\n{sec_data['security']}:")
            print(f"  Success: {sec_data['success']}")
            if sec_data['success']:
                fields = sec_data['fields']
                print(f"  PX_LAST: {fields.get('PX_LAST')}")
    
    # Now test all deltas without D
    print("\n\nTesting all deltas (without D in ticker)...")
    securities = []
    
    # ATM
    securities.append("EURUSDV1M BGN Curncy")
    
    # Risk Reversals and Butterflies for all deltas
    for delta in ["5", "10", "15", "20", "25", "30", "35", "40", "45"]:
        securities.append(f"EURUSD{delta}R1M BGN Curncy")
        securities.append(f"EURUSD{delta}B1M BGN Curncy")
    
    print(f"\nTesting {len(securities)} securities...")
    
    payload = {
        "securities": securities,
        "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
    }
    
    response = requests.post(
        f"{base_url}/api/bloomberg/reference",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        securities_data = data['data']['securities_data']
        
        successful = []
        failed = []
        
        for sec_data in securities_data:
            if sec_data['success']:
                successful.append(sec_data)
            else:
                failed.append(sec_data)
        
        print(f"\nSuccessful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        print("\nSuccessful securities:")
        for sec_data in successful:
            fields = sec_data['fields']
            print(f"  {sec_data['security']}: {fields.get('PX_LAST')}")
        
        if failed:
            print("\nFailed securities:")
            for sec_data in failed[:5]:  # Show first 5
                print(f"  {sec_data['security']}: {sec_data['error']}")


if __name__ == "__main__":
    test_correct_tickers()