#!/usr/bin/env python3
"""
Test Bloomberg Generic Reference Data Endpoint
Tests various securities to see what works
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

def test_reference_data(securities, fields, test_name):
    """Test Bloomberg reference data endpoint"""
    
    print(f"\n{'='*60}")
    print(f"🔍 TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Securities: {securities}")
    print(f"Fields: {fields}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{API_BASE}/api/bloomberg/reference",
            json={
                "securities": securities,
                "fields": fields
            },
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success']:
                print("✅ Request Successful!")
                print(f"Query ID: {data['query_id']}")
                
                # Display results
                if 'securities_data' in data['data']:
                    for sec_data in data['data']['securities_data']:
                        security = sec_data['security']
                        
                        if sec_data['success']:
                            print(f"\n📊 {security}:")
                            for field, value in sec_data['fields'].items():
                                print(f"   {field}: {value}")
                        else:
                            print(f"\n❌ {security}: {sec_data.get('error', 'Unknown error')}")
                
                # Show any errors
                if data['data'].get('errors'):
                    print("\n⚠️  Errors:")
                    for sec, error in data['data']['errors'].items():
                        print(f"   {sec}: {error}")
            else:
                print(f"❌ Request Failed: {data.get('error', {}).get('message', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"🔥 Connection Error: {e}")
    except Exception as e:
        print(f"🔥 Unexpected Error: {e}")

# Run Tests
if __name__ == "__main__":
    print("🚀 BLOOMBERG GENERIC REFERENCE DATA TESTS")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Test 1: FX Spot Rates
    test_reference_data(
        securities=["EURUSD Curncy", "GBPUSD Curncy", "USDJPY Curncy"],
        fields=["PX_LAST", "PX_BID", "PX_ASK"],
        test_name="FX Spot Rates"
    )
    
    # Test 2: FX Volatility - ATM
    test_reference_data(
        securities=["EURUSDV1M BGN Curncy", "EURUSDV3M BGN Curncy"],
        fields=["PX_LAST"],
        test_name="FX ATM Volatility"
    )
    
    # Test 3: FX Volatility - Risk Reversals (Testing different strikes)
    test_reference_data(
        securities=[
            "EURUSD5RR1M BGN Curncy",   # 5 Delta
            "EURUSD10RR1M BGN Curncy",  # 10 Delta
            "EURUSD15RR1M BGN Curncy",  # 15 Delta
            "EURUSD25RR1M BGN Curncy",  # 25 Delta
            "EURUSD35RR1M BGN Curncy"   # 35 Delta
        ],
        fields=["PX_LAST"],
        test_name="FX Risk Reversals - Strike Discovery"
    )
    
    # Test 4: FX Volatility - Butterflies
    test_reference_data(
        securities=[
            "EURUSD10BF1M BGN Curncy",  # 10 Delta
            "EURUSD25BF1M BGN Curncy"   # 25 Delta
        ],
        fields=["PX_LAST"],
        test_name="FX Butterflies"
    )
    
    # Test 5: Invalid Security Test
    test_reference_data(
        securities=["INVALID_TICKER Curncy", "EURUSD Curncy"],
        fields=["PX_LAST"],
        test_name="Error Handling - Invalid Security"
    )
    
    # Test 6: Multiple Fields
    test_reference_data(
        securities=["EURUSD Curncy"],
        fields=["PX_LAST", "PX_BID", "PX_ASK", "PX_OPEN", "PX_HIGH", "PX_LOW", "VOLUME"],
        test_name="Multiple Fields Test"
    )
    
    print(f"\n✅ All tests completed at: {datetime.now()}")