#!/usr/bin/env python3
"""
Simple test of FX volatility data through Bloomberg API
"""

import requests
import json
from datetime import datetime

def test_fx_volatility():
    """Test what FX volatility data is actually available"""
    
    print("📊 Testing FX Volatility Data Access")
    print("=" * 60)
    
    # Test with EURUSD
    print("\n1. Testing EURUSD with basic fields:")
    
    # Start with fields we know work, then add potential vol fields
    basic_payload = {
        "securities": ["EURUSD Curncy"],
        "fields": [
            # Known working fields
            "PX_LAST",
            "PX_BID", 
            "PX_ASK",
            "CHG_PCT_1D",
            
            # Try simple volatility field names
            "VOLATILITY",
            "VOLUME",
            "VWAP",
            
            # Standard deviation / volatility measures
            "STD_DEV_1D",
            "STD_DEV_5D", 
            "STD_DEV_10D",
            "STD_DEV_20D",
            "STD_DEV_30D",
            
            # Price range metrics (proxy for volatility)
            "HIGH_52WEEK",
            "LOW_52WEEK",
            "PRICE_RANGE_1D",
            "PRICE_RANGE_1M",
            
            # Trading range
            "DAY_RANGE",
            "MONTH_RANGE",
            "YEAR_RANGE"
        ]
    }
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json=basic_payload,
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            fields = data['fields']
            
            print("\nAvailable data for EURUSD:")
            for field, value in fields.items():
                if value is not None:
                    print(f"  {field}: {value}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Test FX volatility indices
    print("\n\n2. Testing FX Volatility Indices:")
    
    vol_indices = [
        "EURUSDV1M Index",  # 1-month EURUSD volatility
        "EURUSDV3M Index",  # 3-month EURUSD volatility  
        "EURUSDV6M Index",  # 6-month EURUSD volatility
        "JPYUSDV1M Index",  # 1-month USDJPY volatility
        "GBPUSDV1M Index",  # 1-month GBPUSD volatility
        "CVIX Index",       # Currency volatility index
        "EUVIX Index",      # Euro volatility index
        "BPVIX Index",      # British Pound volatility index
        "JYVIX Index"       # Yen volatility index
    ]
    
    for index in vol_indices:
        payload = {
            "securities": [index],
            "fields": ["PX_LAST", "CHG_PCT_1D", "PX_HIGH", "PX_LOW"]
        }
        
        try:
            response = requests.post(
                "http://20.172.249.92:8080/api/market-data",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]['fields'].get('PX_LAST') is not None:
                    fields = data[0]['fields']
                    print(f"\n✓ {index}:")
                    print(f"  Level: {fields.get('PX_LAST', 'N/A')}")
                    print(f"  Change: {fields.get('CHG_PCT_1D', 'N/A')}%")
                    
        except Exception as e:
            pass
    
    # 3. Test historical data for volatility calculation
    print("\n\n3. Testing Historical Data (for vol calculation):")
    
    # We can calculate volatility from historical prices
    hist_payload = {
        "securities": ["EURUSD Curncy"],
        "fields": ["PX_LAST"],
        "start_date": "2024-12-01",
        "end_date": "2025-01-10"
    }
    
    print("\nTesting historical data endpoint...")
    print("If historical data is available, we can calculate:")
    print("- Historical/realized volatility")
    print("- Price distributions")
    print("- Custom volatility metrics")
    
    # 4. Alternative volatility data sources
    print("\n\n4. Alternative Volatility Indicators:")
    
    # Test currency option tickers
    option_tickers = [
        "EUR Curncy",       # Euro futures
        "GBP Curncy",       # Pound futures
        "JPY Curncy",       # Yen futures
        "EURUSD1M Curncy",  # 1-month forward
        "EURUSD3M Curncy",  # 3-month forward
    ]
    
    for ticker in option_tickers:
        payload = {
            "securities": [ticker],
            "fields": ["PX_LAST", "PX_BID", "PX_ASK", "VOLUME"]
        }
        
        try:
            response = requests.post(
                "http://20.172.249.92:8080/api/market-data",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]['fields'].get('PX_LAST') is not None:
                    fields = data[0]['fields']
                    print(f"\n✓ {ticker}: {fields.get('PX_LAST', 'N/A')}")
                    
        except Exception as e:
            pass
    
    print("\n\n" + "=" * 60)
    print("💡 FX VOLATILITY DATA OPTIONS:")
    print("=" * 60)
    print("""
Based on Bloomberg Terminal access, you can likely:

1. CALCULATE HISTORICAL VOLATILITY
   - Get daily price history
   - Calculate standard deviations
   - Compute realized volatility

2. ACCESS VOLATILITY INDICES
   - Currency-specific vol indices
   - Cross-currency vol measures
   
3. USE PROXY INDICATORS
   - Price ranges (daily, monthly)
   - High/low spreads
   - Trading volumes

4. FX OPTIONS DATA
   - Forward points
   - Option premiums (if available)
   
Would you like me to:
- Set up historical volatility calculations?
- Create a volatility monitoring system?
- Build custom vol indicators?
""")


if __name__ == "__main__":
    test_fx_volatility()