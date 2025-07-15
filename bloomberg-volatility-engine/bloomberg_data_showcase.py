#!/usr/bin/env python3
"""
Showcase all the valuable Bloomberg data we CAN access
"""

import requests
import json
from datetime import datetime
from bloomberg_client import BloombergClient

def showcase_bloomberg_data():
    """Show all the valuable data available through Bloomberg API"""
    
    print("💎 Bloomberg Terminal Data Showcase")
    print("=" * 70)
    print("Demonstrating all valuable data you CAN access with your subscription")
    print("=" * 70)
    
    client = BloombergClient("http://20.172.249.92:8080")
    
    # 1. EQUITY MARKET DATA
    print("\n📈 1. EQUITY MARKET DATA")
    print("-" * 50)
    
    equity_securities = [
        "AAPL US Equity",
        "MSFT US Equity", 
        "GOOGL US Equity",
        "AMZN US Equity",
        "NVDA US Equity"
    ]
    
    equity_fields = [
        "PX_LAST",
        "CHG_PCT_1D", 
        "VOLUME",
        "PX_OPEN",
        "PX_HIGH",
        "PX_LOW",
        "CUR_MKT_CAP",
        "PE_RATIO"
    ]
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json={"securities": equity_securities, "fields": equity_fields},
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            for item in data:
                security = item['security']
                fields = item['fields']
                print(f"\n{security}:")
                print(f"  Price: ${fields.get('PX_LAST', 'N/A')}")
                print(f"  Change: {fields.get('CHG_PCT_1D', 'N/A')}%")
                print(f"  Volume: {fields.get('VOLUME', 'N/A'):,.0f}" if fields.get('VOLUME') else "  Volume: N/A")
                print(f"  Day Range: ${fields.get('PX_LOW', 'N/A')} - ${fields.get('PX_HIGH', 'N/A')}")
                print(f"  Market Cap: ${fields.get('CUR_MKT_CAP', 'N/A'):,.0f}M" if fields.get('CUR_MKT_CAP') else "  Market Cap: N/A")
                print(f"  P/E Ratio: {fields.get('PE_RATIO', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. FX MARKET DATA
    print("\n\n💱 2. FOREIGN EXCHANGE DATA")
    print("-" * 50)
    
    fx_pairs = [
        "EURUSD Curncy",
        "GBPUSD Curncy",
        "USDJPY Curncy",
        "AUDUSD Curncy",
        "USDCAD Curncy",
        "USDCHF Curncy"
    ]
    
    fx_fields = [
        "PX_LAST",
        "PX_BID",
        "PX_ASK",
        "CHG_PCT_1D",
        "PX_HIGH",
        "PX_LOW"
    ]
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json={"securities": fx_pairs, "fields": fx_fields},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\nSpot FX Rates:")
            for item in data:
                pair = item['security'].replace(' Curncy', '')
                fields = item['fields']
                print(f"\n{pair}:")
                print(f"  Rate: {fields.get('PX_LAST', 'N/A')}")
                print(f"  Bid/Ask: {fields.get('PX_BID', 'N/A')} / {fields.get('PX_ASK', 'N/A')}")
                print(f"  Change: {fields.get('CHG_PCT_1D', 'N/A')}%")
                print(f"  Day Range: {fields.get('PX_LOW', 'N/A')} - {fields.get('PX_HIGH', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. COMMODITY DATA
    print("\n\n🛢️ 3. COMMODITY MARKETS")
    print("-" * 50)
    
    commodities = [
        "CL1 Comdty",  # WTI Crude
        "CO1 Comdty",  # Brent Crude
        "GC1 Comdty",  # Gold
        "SI1 Comdty",  # Silver
        "HG1 Comdty",  # Copper
        "NG1 Comdty"   # Natural Gas
    ]
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json={"securities": commodities, "fields": ["PX_LAST", "CHG_PCT_1D", "VOLUME"]},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            commodity_names = {
                "CL1 Comdty": "WTI Crude Oil",
                "CO1 Comdty": "Brent Crude",
                "GC1 Comdty": "Gold",
                "SI1 Comdty": "Silver",
                "HG1 Comdty": "Copper",
                "NG1 Comdty": "Natural Gas"
            }
            
            for item in data:
                security = item['security']
                name = commodity_names.get(security, security)
                fields = item['fields']
                print(f"\n{name}:")
                print(f"  Price: ${fields.get('PX_LAST', 'N/A')}")
                print(f"  Change: {fields.get('CHG_PCT_1D', 'N/A')}%")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. INDEX DATA
    print("\n\n📊 4. MAJOR INDICES")
    print("-" * 50)
    
    indices = [
        "SPX Index",    # S&P 500
        "INDU Index",   # Dow Jones
        "CCMP Index",   # Nasdaq
        "RTY Index",    # Russell 2000
        "VIX Index",    # Volatility
        "DXY Index"     # Dollar Index
    ]
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json={"securities": indices, "fields": ["PX_LAST", "CHG_PCT_1D", "PX_HIGH", "PX_LOW"]},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            index_names = {
                "SPX Index": "S&P 500",
                "INDU Index": "Dow Jones",
                "CCMP Index": "Nasdaq",
                "RTY Index": "Russell 2000",
                "VIX Index": "VIX (Volatility)",
                "DXY Index": "US Dollar Index"
            }
            
            for item in data:
                security = item['security']
                name = index_names.get(security, security)
                fields = item['fields']
                print(f"\n{name}:")
                print(f"  Level: {fields.get('PX_LAST', 'N/A'):,.2f}" if fields.get('PX_LAST') else f"  Level: N/A")
                print(f"  Change: {fields.get('CHG_PCT_1D', 'N/A')}%")
                print(f"  Day Range: {fields.get('PX_LOW', 'N/A'):,.2f} - {fields.get('PX_HIGH', 'N/A'):,.2f}" 
                      if fields.get('PX_LOW') else f"  Day Range: N/A")
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. ECONOMIC INDICATORS
    print("\n\n📉 5. ECONOMIC INDICATORS")
    print("-" * 50)
    
    economic_indicators = [
        "USGG10YR Index",  # 10-Year Treasury
        "USGG2YR Index",   # 2-Year Treasury
        "USGG30YR Index",  # 30-Year Treasury
        "GTDEM10Y Govt",   # German 10Y
        "GTGBP10Y Govt"    # UK 10Y
    ]
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json={"securities": economic_indicators, "fields": ["PX_LAST", "CHG_NET_1D"]},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\nGovernment Bond Yields:")
            for item in data:
                security = item['security']
                fields = item['fields']
                yield_names = {
                    "USGG10YR Index": "US 10-Year",
                    "USGG2YR Index": "US 2-Year", 
                    "USGG30YR Index": "US 30-Year",
                    "GTDEM10Y Govt": "German 10-Year",
                    "GTGBP10Y Govt": "UK 10-Year"
                }
                name = yield_names.get(security, security)
                print(f"  {name}: {fields.get('PX_LAST', 'N/A')}% (Change: {fields.get('CHG_NET_1D', 'N/A')} bps)")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n\n" + "=" * 70)
    print("💡 WHAT YOU CAN DO WITH THIS DATA:")
    print("=" * 70)
    print("""
1. BUILD TRADING STRATEGIES
   - Real-time price alerts
   - Technical analysis systems
   - Pairs trading algorithms
   - Volatility strategies

2. MARKET ANALYSIS
   - Cross-asset correlations
   - Sector rotation analysis
   - Currency strength indicators
   - Commodity trend analysis

3. RISK MANAGEMENT
   - Portfolio risk metrics
   - VaR calculations
   - Hedging strategies
   - Exposure analysis

4. CUSTOM ANALYTICS
   - Build your own indicators
   - Create market dashboards
   - Historical pattern analysis
   - Machine learning models

5. DATA INTEGRATION
   - Store in Cosmos DB
   - Stream to Event Hub
   - Combine with other data sources
   - Build real-time dashboards
""")
    
    print("\n✅ All this data is available with your current Bloomberg subscription!")


if __name__ == "__main__":
    showcase_bloomberg_data()