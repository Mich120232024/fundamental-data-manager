#!/usr/bin/env python3
"""
Test Bloomberg API v5.0 endpoints
Verify the enhanced volatility surface extraction
"""

import requests
import json
from datetime import datetime
import time

def test_api_v5():
    """Test the new API v5 endpoints"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🧪 BLOOMBERG API V5.0 TEST SUITE")
    print("=" * 60)
    print(f"Testing at {datetime.now()}")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. HEALTH CHECK:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Status: {health.get('status')}")
            print(f"✅ Version: {health.get('version')}")
            print(f"✅ Bloomberg Connected: {health.get('bloomberg_connected')}")
            print(f"✅ Mode: {health.get('mode')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # Test 2: Complete volatility surface endpoint
    print("\n\n2. TESTING COMPLETE VOL SURFACE ENDPOINT:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/fx/vol-surface/EURUSD", timeout=30)
        if response.status_code == 200:
            vol_data = response.json()
            print(f"✅ Fields tested: {vol_data.get('fields_tested', 0)}")
            print(f"✅ Fields found: {vol_data.get('fields_found', 0)}")
            
            # Show reference data
            ref_data = vol_data.get('reference_data', {})
            if ref_data:
                print("\n  Reference Data Found:")
                for field, value in list(ref_data.items())[:10]:  # First 10
                    print(f"    - {field}: {value}")
                if len(ref_data) > 10:
                    print(f"    ... and {len(ref_data) - 10} more fields")
            
            # Show option data
            opt_data = vol_data.get('option_data', {})
            if opt_data:
                print("\n  Option Data Found:")
                for field, value in opt_data.items():
                    print(f"    - {field}: {value}")
            
            # Show bulk data
            bulk_data = vol_data.get('bulk_data', {})
            if bulk_data:
                print("\n  Bulk Data Found:")
                for field in bulk_data:
                    print(f"    - {field}: {len(bulk_data[field])} rows")
        else:
            print(f"❌ Vol surface request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Processed volatility surface
    print("\n\n3. TESTING PROCESSED VOL SURFACE:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/fx/vol-surface/EURUSD/processed", timeout=30)
        if response.status_code == 200:
            processed = response.json()
            
            # ATM Vols
            atm_vols = processed.get('atmVols', {})
            if atm_vols:
                print("\n  ATM Volatilities:")
                for tenor, vol in atm_vols.items():
                    print(f"    {tenor}: {vol:.3f}%")
            
            # Risk Reversals
            rr_25d = processed.get('riskReversals', {}).get('25D', {})
            if rr_25d:
                print("\n  25-Delta Risk Reversals:")
                for tenor, rr in rr_25d.items():
                    print(f"    {tenor}: {rr:.3f}")
            else:
                print("\n  ❌ No Risk Reversals found")
            
            # Butterflies
            bf_25d = processed.get('butterflies', {}).get('25D', {})
            if bf_25d:
                print("\n  25-Delta Butterflies:")
                for tenor, bf in bf_25d.items():
                    print(f"    {tenor}: {bf:.3f}")
            else:
                print("\n  ❌ No Butterflies found")
            
            print(f"\n  Raw fields found: {processed.get('raw_fields_found', 0)}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Field discovery
    print("\n\n4. TESTING FIELD DISCOVERY:")
    print("-" * 40)
    
    test_securities = [
        "EURUSD Curncy",
        "EURUSDV1M Curncy",
        "EURUSD1M25C Curncy"
    ]
    
    for security in test_securities:
        try:
            response = requests.get(f"{base_url}/api/discover/{security}", timeout=10)
            if response.status_code == 200:
                discovery = response.json()
                print(f"\n  {security}:")
                print(f"    Fields found: {discovery.get('fields_found', 0)}")
                
                # Show first few fields
                fields = discovery.get('available_fields', {})
                for field, value in list(fields.items())[:5]:
                    print(f"    - {field}: {value}")
        except:
            pass
    
    # Test 5: Enhanced market-data endpoint
    print("\n\n5. TESTING ENHANCED MARKET-DATA ENDPOINT:")
    print("-" * 40)
    
    try:
        response = requests.post(
            f"{base_url}/api/market-data",
            json={
                "securities": ["EURUSD Curncy"],
                "fields": ["25D_RR_1M", "25D_BF_1M", "VOLATILITY_90D"]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print("\n  Enhanced field extraction:")
                for field, value in data[0]["fields"].items():
                    status = "✅" if value is not None else "❌"
                    print(f"    {status} {field}: {value}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 API V5.0 TEST SUMMARY")
    print("=" * 60)
    print("\nThe API v5.0 provides:")
    print("1. /api/fx/vol-surface/<pair> - Raw comprehensive data")
    print("2. /api/fx/vol-surface/<pair>/processed - Calculated RR/BF")
    print("3. /api/discover/<security> - Field discovery")
    print("4. Enhanced /api/market-data - Automatic RR/BF calculation")
    print("\nIf RR/BF are still not available, the Terminal may not")
    print("have the data in the subscription or different field names.")


if __name__ == "__main__":
    test_api_v5()