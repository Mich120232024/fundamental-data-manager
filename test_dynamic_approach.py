#!/usr/bin/env python3
"""
Test Dynamic Bloomberg Approach
Shows how to get ANY data without hardcoding
"""
from bloomberg_dynamic_client import BloombergClient

def test_dynamic_capabilities():
    """Test the dynamic capabilities of the Bloomberg client"""
    
    client = BloombergClient()
    
    print("🚀 DYNAMIC BLOOMBERG CLIENT - NO HARDCODING")
    print("="*60)
    
    # Test 1: Get spot rates dynamically
    print("\n📊 Test 1: Dynamic Spot Rates")
    custom_pairs = ["EURUSD", "GBPJPY", "AUDUSD"]
    spots = client.get_spot_rates(custom_pairs)
    
    if spots.get('success'):
        print(f"✅ Got {len(spots['data']['raw_data'])} spot rates")
        for rate in spots['data']['raw_data']:
            print(f"  {rate['currency_pair']}: {rate['PX_LAST']}")
    else:
        print(f"❌ Spot rates failed: {spots.get('error')}")
    
    # Test 2: Build any volatility surface
    print("\n📈 Test 2: Dynamic Volatility Surface Building")
    
    # Example: I want GBPUSD volatility for specific tenors and deltas
    custom_tenors = ["1M", "3M", "6M"]
    custom_deltas = ["10", "25", "35"]  # Test if 35D works
    
    surface_tickers = client.build_volatility_surface("GBPUSD", custom_tenors, custom_deltas)
    print(f"✅ Built {len(surface_tickers)} volatility tickers:")
    for ticker in surface_tickers[:5]:  # Show first 5
        print(f"  - {ticker}")
    if len(surface_tickers) > 5:
        print(f"  ... and {len(surface_tickers) - 5} more")
    
    # Test 3: Parse any ticker to understand what it is
    print("\n🔍 Test 3: Smart Ticker Parsing")
    test_tickers = [
        "EURUSDV1M Curncy",
        "GBPUSD25RR3M Curncy", 
        "USDJPY10BF6M Curncy",
        "AUDUSD35RR1Y Curncy"
    ]
    
    for ticker in test_tickers:
        parsed = client.parse_vol_ticker(ticker)
        print(f"  {ticker}")
        print(f"    -> {parsed}")
    
    # Test 4: Build tickers for any scenario
    print("\n🏗️  Test 4: Build Tickers for Any Scenario")
    
    scenarios = [
        ("NZDUSD", "2Y", "ATM Vol"),
        ("USDCHF", "15", "3M", "Risk Reversal"),
        ("EURGBP", "50", "6M", "Butterfly")
    ]
    
    for scenario in scenarios:
        if len(scenario) == 3:
            pair, tenor, type_desc = scenario
            ticker = client.build_vol_ticker(pair, tenor)
            print(f"  {type_desc}: {ticker}")
        else:
            pair, delta, tenor, type_desc = scenario
            if "Risk" in type_desc:
                ticker = client.build_rr_ticker(pair, delta, tenor)
            else:
                ticker = client.build_bf_ticker(pair, delta, tenor)
            print(f"  {type_desc}: {ticker}")
    
    print("\n🎯 CONCLUSION:")
    print("- No hardcoding needed")
    print("- Can build ANY Bloomberg ticker dynamically")
    print("- Can parse ANY ticker to understand it")
    print("- Can test ANY combination of pairs/tenors/deltas")
    print("- Just need to deploy the volatility endpoint to test!")

if __name__ == "__main__":
    test_dynamic_capabilities()