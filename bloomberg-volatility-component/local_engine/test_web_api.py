#!/usr/bin/env python3
"""
Test the web API endpoints
"""

import requests
import json

def test_api():
    """Test API endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("Testing Bloomberg Volatility Web API")
    print("=" * 50)
    
    # Test multi-tenor endpoint
    print("\n1. Testing multi-tenor endpoint for EURUSD...")
    try:
        response = requests.get(f"{base_url}/api/volatility/EURUSD")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success: Retrieved {data['success_count']} tenors")
            print(f"   ✓ Failed: {data['failed_count']} tenors")
            
            # Show first few rows
            print("\n   Bloomberg-style data (first 3 rows):")
            for row in data['bloomberg_style'][:3]:
                print(f"   {row['Exp']:>3s}: ATM={row['ATM_Mid']:.3f}, 25RR={row['25D_RR']:.3f}, 25BF={row['25D_BF']:.3f}")
        else:
            print(f"   ✗ Error: Status code {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("   Make sure the web app is running on port 8000")
    
    # Test single tenor endpoint
    print("\n2. Testing single tenor endpoint for EURUSD 1M...")
    try:
        response = requests.get(f"{base_url}/api/volatility/EURUSD/1M")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"   ✓ Success: ATM Mid = {data['atm_mid']:.3f}%")
                print(f"   ✓ 25D RR = {data['rr_25d_mid']:.3f}%")
                print(f"   ✓ 25D BF = {data['bf_25d_mid']:.3f}%")
            else:
                print(f"   ✗ Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ✗ Error: Status code {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


if __name__ == "__main__":
    print("\nNote: Make sure the web app is running first!")
    print("Run: cd local_engine && python3 web_app.py")
    print()
    
    test_api()