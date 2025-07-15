#!/usr/bin/env python3
"""
Test FX volatility data once API server is running
"""

import requests
import json
from datetime import datetime

def test_fx_volatility_live():
    """Test FX volatility with live Bloomberg data"""
    
    print("📊 Testing Live FX Volatility Data")
    print("=" * 60)
    
    # Test basic connection first
    try:
        health = requests.get("http://20.172.249.92:8080/api/health", timeout=5)
        if health.status_code == 200:
            print("✓ API Server is running")
            print(f"✓ Bloomberg connected: {health.json().get('bloomberg_connected')}")
        else:
            print("✗ API Server not responding properly")
            return
    except Exception as e:
        print(f"✗ Cannot connect to API server: {e}")
        return
    
    print("\n1. Testing FX Spot Rates:")
    print("-" * 40)
    
    # Major FX pairs
    fx_pairs = ["EURUSD Curncy", "GBPUSD Curncy", "USDJPY Curncy"]
    
    payload = {
        "securities": fx_pairs,
        "fields": ["PX_LAST", "PX_HIGH", "PX_LOW", "CHG_PCT_1D"]
    }
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            for item in data:
                pair = item['security'].replace(" Curncy", "")
                fields = item['fields']
                print(f"\n{pair}:")
                print(f"  Spot: {fields.get('PX_LAST', 'N/A')}")
                print(f"  Range: {fields.get('PX_LOW', 'N/A')} - {fields.get('PX_HIGH', 'N/A')}")
                print(f"  Change: {fields.get('CHG_PCT_1D', 'N/A')}%")
                
                # Calculate daily range volatility
                if all(fields.get(f) for f in ['PX_HIGH', 'PX_LOW', 'PX_LAST']):
                    range_vol = ((fields['PX_HIGH'] - fields['PX_LOW']) / fields['PX_LAST']) * 100
                    print(f"  Daily Range Vol: {range_vol:.3f}%")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n\n2. Testing Volatility-Specific Fields:")
    print("-" * 40)
    
    # Potential volatility fields to test
    vol_fields = [
        # Standard volatility
        "VOLATILITY_30D",
        "VOLATILITY_90D",
        "HISTORICAL_VOL_30D",
        "IMPLIED_VOL_1M",
        
        # ATM implied vol
        "1M_ATM_IMP_VOL",
        "3M_ATM_IMP_VOL",
        
        # Risk reversal
        "25D_RR_1M",
        "25D_BF_1M",
        
        # Simple vol metrics
        "HV30",
        "IV30",
        "REALIZED_VOL"
    ]
    
    test_payload = {
        "securities": ["EURUSD Curncy"],
        "fields": vol_fields
    }
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json=test_payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            fields = data['fields']
            
            print("\nAvailable Volatility Fields:")
            found_any = False
            for field in vol_fields:
                if field in fields and fields[field] is not None:
                    print(f"  ✓ {field}: {fields[field]}")
                    found_any = True
            
            if not found_any:
                print("  No direct volatility fields found")
                print("  Will need to calculate from price data")
    except Exception as e:
        print(f"Error testing vol fields: {e}")
    
    print("\n\n3. Testing FX Options/Volatility Products:")
    print("-" * 40)
    
    # Test volatility index or option products
    vol_products = [
        "EURUSDV1M Index",
        "EURUSDV3M Index", 
        "EUR1M Curncy",
        "EUR3M Curncy",
        "CVIX Index"
    ]
    
    for product in vol_products:
        try:
            response = requests.post(
                "http://20.172.249.92:8080/api/market-data",
                json={"securities": [product], "fields": ["PX_LAST"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]['fields'].get('PX_LAST') is not None:
                    print(f"  ✓ {product}: {data[0]['fields']['PX_LAST']}")
        except:
            pass
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY: Available FX Volatility Data")
    print("=" * 60)


if __name__ == "__main__":
    test_fx_volatility_live()