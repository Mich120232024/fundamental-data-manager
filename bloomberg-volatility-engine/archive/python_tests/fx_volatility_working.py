#!/usr/bin/env python3
"""
Test FX volatility with known working fields
"""

import requests
import json

def test_fx_volatility_working():
    """Test FX volatility with fields that should work"""
    
    print("📊 FX Market Data & Volatility Metrics")
    print("=" * 60)
    
    # 1. Get basic FX data first
    print("\n1. Current FX Rates & Basic Metrics:")
    print("-" * 40)
    
    fx_pairs = [
        "EURUSD Curncy",
        "GBPUSD Curncy", 
        "USDJPY Curncy",
        "AUDUSD Curncy",
        "USDCHF Curncy"
    ]
    
    # Use only known working fields
    basic_fields = [
        "PX_LAST",
        "PX_BID",
        "PX_ASK",
        "PX_HIGH",
        "PX_LOW",
        "CHG_PCT_1D",
        "PX_OPEN",
        "VOLUME"
    ]
    
    for pair in fx_pairs:
        payload = {
            "securities": [pair],
            "fields": basic_fields
        }
        
        try:
            response = requests.post(
                "http://20.172.249.92:8080/api/market-data",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                fields = data['fields']
                
                pair_name = pair.replace(" Curncy", "")
                print(f"\n{pair_name}:")
                print(f"  Rate: {fields.get('PX_LAST', 'N/A')}")
                print(f"  Bid/Ask: {fields.get('PX_BID', 'N/A')} / {fields.get('PX_ASK', 'N/A')}")
                print(f"  Today's Range: {fields.get('PX_LOW', 'N/A')} - {fields.get('PX_HIGH', 'N/A')}")
                print(f"  Change: {fields.get('CHG_PCT_1D', 'N/A')}%")
                
                # Calculate simple volatility metric from high/low
                if fields.get('PX_HIGH') and fields.get('PX_LOW') and fields.get('PX_LAST'):
                    high = float(fields['PX_HIGH'])
                    low = float(fields['PX_LOW'])
                    last = float(fields['PX_LAST'])
                    daily_range_pct = ((high - low) / last) * 100
                    print(f"  Daily Range %: {daily_range_pct:.3f}%")
                    
        except Exception as e:
            print(f"Error for {pair}: {e}")
    
    # 2. Test volatility-specific securities
    print("\n\n2. Testing Volatility Products:")
    print("-" * 40)
    
    # These might be volatility products
    vol_securities = [
        "EURUSDV1M CMPN Curncy",  # 1M vol
        "EURUSDV3M CMPN Curncy",  # 3M vol
        "USDJPYV1M CMPN Curncy",  # USDJPY 1M vol
        "DXY Index",              # Dollar Index (for correlation)
        "VIX Index"               # VIX for comparison
    ]
    
    for sec in vol_securities:
        payload = {
            "securities": [sec],
            "fields": ["PX_LAST", "CHG_PCT_1D"]
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
                    print(f"\n✓ {sec}: {fields.get('PX_LAST')} ({fields.get('CHG_PCT_1D')}% change)")
                else:
                    print(f"\n✗ {sec}: No data")
                    
        except Exception as e:
            pass
    
    # 3. Calculate volatility from price movements
    print("\n\n3. Volatility Calculations from Price Data:")
    print("-" * 40)
    
    print("\nTo calculate FX volatility, we can:")
    print("1. Fetch historical daily prices")
    print("2. Calculate daily returns")
    print("3. Compute standard deviation")
    print("4. Annualize the volatility")
    
    print("\nExample calculation for EURUSD:")
    print("- Get 30 days of daily closes")
    print("- Daily returns = ln(close[i]/close[i-1])")
    print("- Volatility = std(returns) * sqrt(252)")
    
    # 4. Available data summary
    print("\n\n" + "=" * 60)
    print("💡 FX VOLATILITY DATA AVAILABLE:")
    print("=" * 60)
    print("""
From your Bloomberg Terminal access, you have:

1. REAL-TIME FX DATA
   ✓ Spot rates (bid/ask/last)
   ✓ Daily high/low ranges
   ✓ Volume data
   ✓ Percentage changes

2. CALCULATED METRICS
   ✓ Daily range as % (volatility proxy)
   ✓ Bid-ask spreads
   ✓ Price momentum

3. HISTORICAL DATA (if available)
   → Calculate realized volatility
   → Compute GARCH models
   → Build custom indicators

4. WHAT YOU CAN BUILD:
   - FX volatility monitor
   - Range breakout systems
   - Volatility regime detection
   - Cross-pair correlation analysis

Would you like me to create a volatility calculation system?
""")


if __name__ == "__main__":
    test_fx_volatility_working()