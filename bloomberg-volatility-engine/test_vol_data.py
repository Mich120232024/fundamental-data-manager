#!/usr/bin/env python3
"""
Test Bloomberg volatility data to compare with terminal
"""

import requests
import json
from datetime import datetime

BLOOMBERG_API = "http://20.172.249.92:8080"

def test_atm_vols():
    """Test ATM volatility data"""
    print("=== Testing ATM Volatilities ===")
    
    # Test specific tenors that match Bloomberg screen
    tenors = ['1W', '2W', '1M', '2M', '3M', '6M', '1Y']
    
    for tenor in tenors:
        ticker = f"EURUSDV{tenor} Curncy"
        payload = {
            "securities": [ticker],
            "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
        }
        
        try:
            response = requests.post(f"{BLOOMBERG_API}/api/market-data", json=payload)
            if response.ok:
                data = response.json()
                if data and len(data) > 0:
                    fields = data[0]['fields']
                    print(f"{tenor}: Bid={fields.get('PX_BID', 'N/A')}, Ask={fields.get('PX_ASK', 'N/A')}, Last={fields.get('PX_LAST', 'N/A')}")
                else:
                    print(f"{tenor}: No data")
        except Exception as e:
            print(f"{tenor}: Error - {e}")

def test_risk_reversals():
    """Test risk reversal data"""
    print("\n=== Testing 25D Risk Reversals ===")
    
    tenors = ['1W', '2W', '1M', '2M', '3M', '6M', '1Y']
    
    for tenor in tenors:
        ticker = f"EUR25R{tenor} Curncy"
        payload = {
            "securities": [ticker],
            "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
        }
        
        try:
            response = requests.post(f"{BLOOMBERG_API}/api/market-data", json=payload)
            if response.ok:
                data = response.json()
                if data and len(data) > 0:
                    fields = data[0]['fields']
                    print(f"{tenor}: Bid={fields.get('PX_BID', 'N/A')}, Ask={fields.get('PX_ASK', 'N/A')}, Last={fields.get('PX_LAST', 'N/A')}")
                else:
                    print(f"{tenor}: No data")
        except Exception as e:
            print(f"{tenor}: Error - {e}")

def test_butterflies():
    """Test butterfly data"""
    print("\n=== Testing 25D Butterflies ===")
    
    tenors = ['1W', '2W', '1M', '2M', '3M', '6M', '1Y']
    
    for tenor in tenors:
        ticker = f"EUR25B{tenor} Curncy"
        payload = {
            "securities": [ticker],
            "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
        }
        
        try:
            response = requests.post(f"{BLOOMBERG_API}/api/market-data", json=payload)
            if response.ok:
                data = response.json()
                if data and len(data) > 0:
                    fields = data[0]['fields']
                    print(f"{tenor}: Bid={fields.get('PX_BID', 'N/A')}, Ask={fields.get('PX_ASK', 'N/A')}, Last={fields.get('PX_LAST', 'N/A')}")
                else:
                    print(f"{tenor}: No data")
        except Exception as e:
            print(f"{tenor}: Error - {e}")

def calculate_smile():
    """Calculate sample smile values"""
    print("\n=== Calculated Smile for 1M ===")
    
    # Get 1M data
    atm_response = requests.post(f"{BLOOMBERG_API}/api/market-data", 
                                json={"securities": ["EURUSDV1M Curncy"], "fields": ["PX_LAST"]})
    rr_response = requests.post(f"{BLOOMBERG_API}/api/market-data",
                               json={"securities": ["EUR25R1M Curncy"], "fields": ["PX_LAST"]})
    bf_response = requests.post(f"{BLOOMBERG_API}/api/market-data",
                               json={"securities": ["EUR25B1M Curncy"], "fields": ["PX_LAST"]})
    
    if atm_response.ok and rr_response.ok and bf_response.ok:
        atm = atm_response.json()[0]['fields'].get('PX_LAST', 0)
        rr = rr_response.json()[0]['fields'].get('PX_LAST', 0)
        bf = bf_response.json()[0]['fields'].get('PX_LAST', 0)
        
        print(f"ATM: {atm}")
        print(f"25D RR: {rr}")
        print(f"25D BF: {bf}")
        print(f"\nCalculated:")
        print(f"25D Put: {atm - 0.5 * rr + bf:.3f}")
        print(f"ATM: {atm:.3f}")
        print(f"25D Call: {atm + 0.5 * rr + bf:.3f}")

if __name__ == "__main__":
    print(f"Testing Bloomberg Vol Data - {datetime.now()}")
    print("=" * 60)
    
    test_atm_vols()
    test_risk_reversals()
    test_butterflies()
    calculate_smile()