#!/usr/bin/env python3
"""
Explore all available FX volatility data in Bloomberg
"""

import requests
import json
from datetime import datetime
from tabulate import tabulate

def explore_fx_volatility():
    """Deep dive into FX volatility data available through Bloomberg"""
    
    print("📊 Bloomberg FX Volatility Data Explorer")
    print("=" * 80)
    print("Discovering all volatility metrics available for FX markets")
    print("=" * 80)
    
    # Major FX pairs to test
    fx_pairs = [
        "EURUSD Curncy",
        "GBPUSD Curncy",
        "USDJPY Curncy",
        "AUDUSD Curncy",
        "USDCHF Curncy",
        "USDCAD Curncy",
        "NZDUSD Curncy",
        "EURGBP Curncy",
        "EURJPY Curncy"
    ]
    
    # 1. IMPLIED VOLATILITY DATA
    print("\n📈 1. IMPLIED VOLATILITY (Options Market)")
    print("-" * 60)
    
    iv_fields = [
        # At-the-money implied volatilities
        "VOLATILITY_10D",          # 10-day implied vol
        "VOLATILITY_20D",          # 20-day implied vol  
        "VOLATILITY_30D",          # 30-day implied vol
        "VOLATILITY_60D",          # 60-day implied vol
        "VOLATILITY_90D",          # 90-day implied vol
        "VOLATILITY_180D",         # 180-day implied vol
        "VOLATILITY_360D",         # 360-day implied vol
        
        # ATM volatilities by tenor
        "1M_ATM_IMP_VOL",          # 1-month ATM implied vol
        "2M_ATM_IMP_VOL",          # 2-month ATM implied vol
        "3M_ATM_IMP_VOL",          # 3-month ATM implied vol
        "6M_ATM_IMP_VOL",          # 6-month ATM implied vol
        "1Y_ATM_IMP_VOL",          # 1-year ATM implied vol
        
        # Volatility surface data
        "25D_RISK_REVERSAL_1M",    # 25-delta risk reversal 1M
        "25D_BUTTERFLY_1M",        # 25-delta butterfly 1M
        "10D_RISK_REVERSAL_1M",    # 10-delta risk reversal 1M
        "10D_BUTTERFLY_1M",        # 10-delta butterfly 1M
        
        # Vol of vol
        "IMP_VOL_OF_VOL",          # Implied volatility of volatility
        "ATM_IMP_VOL_1M_CHG",      # Change in 1M ATM vol
    ]
    
    # Test with EURUSD first
    test_pair = "EURUSD Curncy"
    payload = {
        "securities": [test_pair],
        "fields": iv_fields
    }
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            fields = data['fields']
            
            print(f"\nImplied Volatility data for {test_pair}:")
            available_iv = []
            
            for field in iv_fields:
                if field in fields and fields[field] is not None:
                    available_iv.append([field, fields[field]])
                    
            if available_iv:
                print(tabulate(available_iv, headers=["Field", "Value"], tablefmt="grid"))
            else:
                print("No implied volatility fields available")
                
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. HISTORICAL/REALIZED VOLATILITY
    print("\n\n📊 2. HISTORICAL/REALIZED VOLATILITY")
    print("-" * 60)
    
    hist_vol_fields = [
        "VOLATILITY_10D_CALC",     # 10-day historical volatility
        "VOLATILITY_20D_CALC",     # 20-day historical volatility
        "VOLATILITY_30D_CALC",     # 30-day historical volatility
        "VOLATILITY_60D_CALC",     # 60-day historical volatility
        "VOLATILITY_90D_CALC",     # 90-day historical volatility
        "VOLATILITY_260D_CALC",    # 260-day (1Y) historical volatility
        
        "HIST_VOL_10D",            # Alternative historical vol fields
        "HIST_VOL_20D",
        "HIST_VOL_30D",
        "HIST_VOL_60D",
        
        "REALIZED_VOL_10D",        # Realized volatility
        "REALIZED_VOL_20D",
        "REALIZED_VOL_30D",
        
        "VOLATILITY_RATIO",        # Implied/Realized ratio
        "VOL_PREMIUM",             # Volatility premium
    ]
    
    payload = {
        "securities": [test_pair],
        "fields": hist_vol_fields
    }
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            fields = data['fields']
            
            print(f"\nHistorical Volatility data for {test_pair}:")
            available_hist = []
            
            for field in hist_vol_fields:
                if field in fields and fields[field] is not None:
                    available_hist.append([field, fields[field]])
                    
            if available_hist:
                print(tabulate(available_hist, headers=["Field", "Value"], tablefmt="grid"))
            else:
                print("No historical volatility fields available")
                
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. VOLATILITY ANALYTICS
    print("\n\n📉 3. VOLATILITY ANALYTICS & GREEKS")
    print("-" * 60)
    
    vol_analytics_fields = [
        # Term structure
        "VOL_TERM_STRUCTURE",      # Volatility term structure
        "VOL_CURVE_SLOPE",         # Slope of vol curve
        
        # Skew metrics
        "VOL_SKEW_25D",            # 25-delta volatility skew
        "VOL_SKEW_10D",            # 10-delta volatility skew
        "PUT_CALL_VOL_SPREAD",     # Put-Call vol spread
        
        # Greeks and sensitivities
        "VEGA_1M_ATM",             # Vega for 1M ATM option
        "VANNA_1M_ATM",            # Vanna (dVega/dSpot)
        "VOLGA_1M_ATM",            # Volga (dVega/dVol)
        
        # Correlation metrics
        "CORRELATION_SPX_30D",     # Correlation with S&P 500
        "CORRELATION_DXY_30D",     # Correlation with Dollar Index
        
        # Other vol metrics
        "GARCH_VOL_FORECAST",      # GARCH volatility forecast
        "STOCHASTIC_VOL",          # Stochastic volatility
        "LOCAL_VOL",               # Local volatility
    ]
    
    payload = {
        "securities": [test_pair],
        "fields": vol_analytics_fields
    }
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()[0]
            fields = data['fields']
            
            print(f"\nVolatility Analytics for {test_pair}:")
            available_analytics = []
            
            for field in vol_analytics_fields:
                if field in fields and fields[field] is not None:
                    available_analytics.append([field, fields[field]])
                    
            if available_analytics:
                print(tabulate(available_analytics, headers=["Field", "Value"], tablefmt="grid"))
                
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. TEST ALL MAJOR PAIRS
    print("\n\n🌍 4. VOLATILITY ACROSS MAJOR FX PAIRS")
    print("-" * 60)
    
    # Key volatility fields to check across all pairs
    key_vol_fields = [
        "VOLATILITY_30D",
        "VOLATILITY_90D", 
        "1M_ATM_IMP_VOL",
        "VOLATILITY_30D_CALC",
        "25D_RISK_REVERSAL_1M"
    ]
    
    all_pairs_data = []
    
    for pair in fx_pairs:
        payload = {
            "securities": [pair],
            "fields": key_vol_fields + ["PX_LAST"]
        }
        
        try:
            response = requests.post(
                "http://20.172.249.92:8080/api/market-data",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()[0]
                fields = data['fields']
                
                pair_data = {
                    "Pair": pair.replace(" Curncy", ""),
                    "Spot": fields.get("PX_LAST", "N/A")
                }
                
                # Add available vol fields
                for field in key_vol_fields:
                    if field in fields and fields[field] is not None:
                        # Shorten field names for display
                        display_name = field.replace("VOLATILITY_", "").replace("_CALC", "_HIST")
                        pair_data[display_name] = f"{fields[field]:.2f}" if isinstance(fields[field], (int, float)) else fields[field]
                
                all_pairs_data.append(pair_data)
                
        except Exception as e:
            print(f"Error for {pair}: {e}")
    
    if all_pairs_data:
        print("\nVolatility Summary Across FX Pairs:")
        # Get all unique columns
        all_columns = []
        for d in all_pairs_data:
            all_columns.extend(d.keys())
        unique_columns = list(dict.fromkeys(all_columns))
        
        # Create table data
        table_data = []
        for pair_data in all_pairs_data:
            row = [pair_data.get(col, "N/A") for col in unique_columns]
            table_data.append(row)
        
        print(tabulate(table_data, headers=unique_columns, tablefmt="grid"))
    
    # 5. FX OPTIONS DATA
    print("\n\n🎯 5. FX OPTIONS & VOLATILITY SURFACE")
    print("-" * 60)
    
    # Test FX option chains
    option_test = "EURUSD 1M 100 Call Curncy"  # Example FX option
    
    payload = {
        "securities": [option_test],
        "fields": ["PX_LAST", "IMPLIED_VOLATILITY", "DELTA", "VEGA", "THETA", "GAMMA"]
    }
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✓ FX Options data available")
        else:
            print("✗ FX Options data may require additional setup")
            
    except Exception as e:
        print(f"FX Options test: {e}")
    
    print("\n\n" + "=" * 80)
    print("💡 FX VOLATILITY DATA SUMMARY")
    print("=" * 80)
    print("""
Based on the exploration, you likely have access to:

1. IMPLIED VOLATILITY
   - ATM implied vols (1M, 2M, 3M, 6M, 1Y)
   - Volatility term structure
   - Risk reversals and butterflies
   - Volatility smile/skew data

2. HISTORICAL VOLATILITY
   - Realized volatility (10D, 20D, 30D, 60D, 90D)
   - GARCH and other vol models
   - Vol ratios and premiums

3. VOLATILITY ANALYTICS
   - Greeks (Vega, Vanna, Volga)
   - Correlation matrices
   - Vol forecasts and models

4. TRADEABLE PRODUCTS
   - FX options chains
   - Volatility swaps
   - Variance swaps

This data enables:
- Volatility trading strategies
- Options pricing and hedging
- Risk management
- Market timing based on vol regimes
""")


if __name__ == "__main__":
    explore_fx_volatility()