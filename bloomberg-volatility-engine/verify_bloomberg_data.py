#!/usr/bin/env python3
"""
Direct comparison with Bloomberg Terminal data
"""

import requests
import json
from datetime import datetime

BLOOMBERG_API = "http://20.172.249.92:8080"

def get_exact_bloomberg_data():
    """Get the exact data Bloomberg Terminal shows"""
    print("=== EXACT BLOOMBERG TERMINAL DATA ===")
    print(f"Time: {datetime.now()}")
    print()
    
    # Test the exact tickers we're using in the React app
    tenors = ['1W', '1M', '3M', '6M', '1Y']
    
    print("1. ATM VOLATILITIES:")
    atm_data = {}
    for tenor in tenors:
        ticker = f"EURUSDV{tenor} Curncy"
        try:
            response = requests.post(f"{BLOOMBERG_API}/api/market-data", 
                                   json={"securities": [ticker], "fields": ["PX_LAST", "PX_BID", "PX_ASK"]})
            if response.ok and response.json():
                fields = response.json()[0]['fields']
                atm_data[tenor] = fields.get('PX_LAST', 0)
                print(f"  {tenor}: {fields.get('PX_LAST', 'N/A')}% (Bid: {fields.get('PX_BID', 'N/A')}, Ask: {fields.get('PX_ASK', 'N/A')})")
        except Exception as e:
            print(f"  {tenor}: ERROR - {e}")
    
    print("\n2. 25D RISK REVERSALS:")
    rr_data = {}
    for tenor in tenors:
        ticker = f"EUR25R{tenor} Curncy"
        try:
            response = requests.post(f"{BLOOMBERG_API}/api/market-data", 
                                   json={"securities": [ticker], "fields": ["PX_LAST"]})
            if response.ok and response.json():
                fields = response.json()[0]['fields']
                rr_data[tenor] = fields.get('PX_LAST', 0)
                print(f"  {tenor}: {fields.get('PX_LAST', 'N/A')}%")
        except Exception as e:
            print(f"  {tenor}: ERROR - {e}")
    
    print("\n3. 25D BUTTERFLIES:")
    bf_data = {}
    for tenor in tenors:
        ticker = f"EUR25B{tenor} Curncy"
        try:
            response = requests.post(f"{BLOOMBERG_API}/api/market-data", 
                                   json={"securities": [ticker], "fields": ["PX_LAST"]})
            if response.ok and response.json():
                fields = response.json()[0]['fields']
                bf_data[tenor] = fields.get('PX_LAST', 0)
                print(f"  {tenor}: {fields.get('PX_LAST', 'N/A')}%")
        except Exception as e:
            print(f"  {tenor}: ERROR - {e}")
    
    print("\n4. CALCULATED SMILE (Standard FX Formulas):")
    print("Tenor\t25D Put\t\tATM\t\t25D Call\tSmile Width")
    print("-" * 60)
    
    for tenor in tenors:
        if tenor in atm_data and tenor in rr_data and tenor in bf_data:
            atm = atm_data[tenor]
            rr = rr_data[tenor]
            bf = bf_data[tenor]
            
            put25 = atm - 0.5 * rr + bf
            call25 = atm + 0.5 * rr + bf
            smile_width = put25 - atm
            
            print(f"{tenor}\t{put25:.3f}%\t\t{atm:.3f}%\t\t{call25:.3f}%\t\t{smile_width:.3f}%")
    
    print("\n5. SURFACE VALIDATION:")
    print("Expected volatility range:", f"{min(atm_data.values()):.3f}% to {max([atm_data[t] - 0.5 * rr_data[t] + bf_data[t] for t in tenors if t in atm_data]):.3f}%")
    
    return atm_data, rr_data, bf_data

if __name__ == "__main__":
    get_exact_bloomberg_data()