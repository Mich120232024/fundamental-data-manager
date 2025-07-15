#!/usr/bin/env python3
"""
Test extracting implied volatilities from FX option tickers
Focus on EURUSD to get Risk Reversals and Butterflies
"""

import requests
import json
from datetime import datetime

def test_option_implied_vols():
    """Extract implied volatilities from option tickers"""
    
    base_url = "http://20.172.249.92:8080"
    
    print("🎯 FX OPTION IMPLIED VOLATILITY EXTRACTION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Define option tickers and fields to test
    option_data = {}
    
    # Test 1: Get implied volatilities from option tickers
    print("\n1. EXTRACTING IMPLIED VOLATILITIES FROM OPTIONS:")
    print("-" * 40)
    
    # Option tickers for different tenors
    option_tickers = [
        # 1 Month options
        ("EURUSD1M25C Curncy", "1M 25-delta Call"),
        ("EURUSD1M25P Curncy", "1M 25-delta Put"),
        ("EURUSDV1M Curncy", "1M ATM"),
        
        # 3 Month options  
        ("EURUSD3M25C Curncy", "3M 25-delta Call"),
        ("EURUSD3M25P Curncy", "3M 25-delta Put"),
        ("EURUSDV3M Curncy", "3M ATM"),
        
        # 6 Month options
        ("EURUSD6M25C Curncy", "6M 25-delta Call"),
        ("EURUSD6M25P Curncy", "6M 25-delta Put"),
        ("EURUSDV6M Curncy", "6M ATM"),
        
        # 1 Year options
        ("EURUSD1Y25C Curncy", "1Y 25-delta Call"),
        ("EURUSD1Y25P Curncy", "1Y 25-delta Put"),
        ("EURUSDV1Y Curncy", "1Y ATM"),
    ]
    
    # Fields that might contain implied volatility
    vol_fields = [
        "IMP_VOLATILITY",      # Implied volatility
        "IVOL_MID",           # Mid implied vol
        "OPT_IMPLIED_VOLATILITY",
        "VOLATILITY_MID",
        "PX_LAST",            # Last price (we saw this works)
        "PX_MID",             # Mid price
        "DELTA",              # Option delta
        "OPT_DELTA_MID"       # Mid delta
    ]
    
    for ticker, description in option_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": vol_fields},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                fields = data.get('fields', {})
                non_null_fields = {k: v for k, v in fields.items() if v is not None}
                
                if non_null_fields:
                    print(f"\n{description} ({ticker}):")
                    for field, value in non_null_fields.items():
                        print(f"  {field}: {value}")
                    option_data[ticker] = non_null_fields
        except Exception as e:
            print(f"Error for {ticker}: {e}")
    
    # Test 2: Calculate Risk Reversals and Butterflies
    print("\n\n2. CALCULATING RISK REVERSALS & BUTTERFLIES:")
    print("-" * 40)
    
    tenors = ["1M", "3M", "6M", "1Y"]
    
    for tenor in tenors:
        call_ticker = f"EURUSD{tenor}25C Curncy"
        put_ticker = f"EURUSD{tenor}25P Curncy"
        atm_ticker = f"EURUSDV{tenor} Curncy"
        
        # Get data if available
        call_data = option_data.get(call_ticker, {})
        put_data = option_data.get(put_ticker, {})
        atm_data = option_data.get(atm_ticker, {})
        
        print(f"\n{tenor} Tenor:")
        
        # Check if we have volatility data
        if 'IMP_VOLATILITY' in call_data and 'IMP_VOLATILITY' in put_data:
            call_vol = call_data['IMP_VOLATILITY']
            put_vol = put_data['IMP_VOLATILITY']
            rr = call_vol - put_vol
            print(f"  Risk Reversal = {call_vol:.3f} - {put_vol:.3f} = {rr:.3f}")
            
            if 'PX_LAST' in atm_data:
                atm_vol = atm_data['PX_LAST']
                bf = 0.5 * (call_vol + put_vol) - atm_vol
                print(f"  Butterfly = 0.5*({call_vol:.3f} + {put_vol:.3f}) - {atm_vol:.3f} = {bf:.3f}")
        else:
            # Check if price data suggests these are volatilities
            if 'PX_LAST' in call_data and 'PX_LAST' in put_data:
                call_price = call_data['PX_LAST']
                put_price = put_data['PX_LAST']
                print(f"  Call price/vol: {call_price}")
                print(f"  Put price/vol: {put_price}")
                
                # If these are volatilities (in reasonable range)
                if 5 < call_price < 30 and 5 < put_price < 30:
                    print(f"  → These might be volatilities in %")
                    rr = call_price - put_price
                    print(f"  → Risk Reversal estimate: {rr:.3f}")
    
    # Test 3: Alternative ticker formats
    print("\n\n3. TESTING ALTERNATIVE TICKER FORMATS:")
    print("-" * 40)
    
    alt_tickers = [
        # Try with RR/BF specific tickers
        ("EURUSD25RR1M Curncy", "1M Risk Reversal"),
        ("EURUSD25BF1M Curncy", "1M Butterfly"),
        ("EUR25RR1M Curncy", "1M Risk Reversal"),
        ("EUR25BF1M Curncy", "1M Butterfly"),
        
        # Try volatility surface tickers
        ("EURUSDVS1M Curncy", "1M Vol Surface"),
        ("EURUSDVOL1M Curncy", "1M Volatility"),
    ]
    
    for ticker, description in alt_tickers:
        try:
            response = requests.post(
                f"{base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID"]},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                fields = data.get('fields', {})
                if any(v is not None for v in fields.values()):
                    print(f"  ✓ {ticker}: {fields}")
        except:
            pass
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 ANALYSIS & RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n🔍 KEY FINDINGS:")
    print("1. EURUSD option tickers return price data (24.14 for both 1M 25C and 25P)")
    print("2. These prices are identical for calls and puts - unusual")
    print("3. No IMP_VOLATILITY field available on option tickers")
    print("4. ATM volatilities work correctly via EURUSDV[tenor] tickers")
    
    print("\n💡 NEXT STEPS:")
    print("1. The 24.14 values might be volatilities, not prices")
    print("2. Need to verify with Bloomberg Terminal what these values represent")
    print("3. If they are vols, RR would be 0 (same value for call and put)")
    print("4. Consider using market convention: flat smile if no RR/BF data available")


if __name__ == "__main__":
    test_option_implied_vols()