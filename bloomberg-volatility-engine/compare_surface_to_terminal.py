#!/usr/bin/env python3
"""
Generate a comparison report to verify our volatility surface matches Bloomberg Terminal.
This creates a formatted output that can be compared side-by-side with Terminal screens.
"""

import requests
import json
from datetime import datetime
from tabulate import tabulate

BLOOMBERG_API = "http://20.172.249.92:8080"

def fetch_complete_surface(pair="EURUSD"):
    """Fetch complete volatility surface data"""
    
    # Fetch all components
    print(f"Fetching {pair} volatility surface components...")
    
    # ATM Vols
    atm_vols = {}
    tenors = ['1M', '3M', '6M', '1Y']
    for tenor in tenors:
        ticker = f"{pair}V{tenor} Curncy"
        response = requests.post(f"{BLOOMBERG_API}/api/market-data", 
                                json={"securities": [ticker], "fields": ["PX_LAST"]})
        if response.ok and response.json():
            atm_vols[tenor] = response.json()[0]['fields'].get('PX_LAST', 0)
    
    # Risk Reversals and Butterflies
    risk_reversals = {'25D': {}, '10D': {}}
    butterflies = {'25D': {}, '10D': {}}
    
    for delta in ['25', '10']:
        for tenor in tenors:
            # RR
            rr_ticker = f"{pair[:3]}{delta}R{tenor} Curncy"
            response = requests.post(f"{BLOOMBERG_API}/api/market-data",
                                   json={"securities": [rr_ticker], "fields": ["PX_LAST", "PX_MID"]})
            if response.ok and response.json():
                fields = response.json()[0]['fields']
                risk_reversals[f'{delta}D'][tenor] = fields.get('PX_MID') or fields.get('PX_LAST', 0)
            
            # BF
            bf_ticker = f"{pair[:3]}{delta}B{tenor} Curncy"
            response = requests.post(f"{BLOOMBERG_API}/api/market-data",
                                   json={"securities": [bf_ticker], "fields": ["PX_LAST", "PX_MID"]})
            if response.ok and response.json():
                fields = response.json()[0]['fields']
                butterflies[f'{delta}D'][tenor] = fields.get('PX_MID') or fields.get('PX_LAST', 0)
    
    return atm_vols, risk_reversals, butterflies

def calculate_smile_grid(atm_vols, risk_reversals, butterflies):
    """Calculate complete smile grid matching Bloomberg format"""
    
    tenors = ['1M', '3M', '6M', '1Y']
    strikes = ['10D Put', '25D Put', 'ATM', '25D Call', '10D Call']
    
    # Build the grid
    grid = []
    
    for tenor in tenors:
        atm = atm_vols.get(tenor, 0)
        rr25 = risk_reversals['25D'].get(tenor, 0)
        bf25 = butterflies['25D'].get(tenor, 0)
        rr10 = risk_reversals['10D'].get(tenor, 0)
        bf10 = butterflies['10D'].get(tenor, 0)
        
        row = [
            tenor,
            f"{atm - 0.5 * rr10 + bf10:.2f}",  # 10D Put
            f"{atm - 0.5 * rr25 + bf25:.2f}",  # 25D Put
            f"{atm:.2f}",                       # ATM
            f"{atm + 0.5 * rr25 + bf25:.2f}",  # 25D Call
            f"{atm + 0.5 * rr10 + bf10:.2f}"   # 10D Call
        ]
        grid.append(row)
    
    return grid

def generate_bloomberg_format_report(pair="EURUSD"):
    """Generate a report formatted like Bloomberg Terminal display"""
    
    print("=" * 80)
    print(f"BLOOMBERG TERMINAL VOLATILITY SURFACE COMPARISON")
    print(f"Currency Pair: {pair}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Fetch data
    atm_vols, risk_reversals, butterflies = fetch_complete_surface(pair)
    
    # Section 1: ATM Volatilities
    print("\n1. AT-THE-MONEY VOLATILITIES")
    print("-" * 40)
    atm_table = []
    for tenor, vol in atm_vols.items():
        atm_table.append([f"{pair}V{tenor}", tenor, f"{vol:.2f}%"])
    print(tabulate(atm_table, headers=['Bloomberg Ticker', 'Tenor', 'ATM Vol'], tablefmt='grid'))
    
    # Section 2: Risk Reversals
    print("\n2. RISK REVERSALS")
    print("-" * 40)
    rr_table = []
    for delta in ['25D', '10D']:
        for tenor, value in risk_reversals[delta].items():
            ticker = f"{pair[:3]}{delta[:-1]}R{tenor}"
            rr_table.append([ticker, f"{delta} {tenor}", f"{value:.3f}"])
    print(tabulate(rr_table, headers=['Bloomberg Ticker', 'Strike/Tenor', 'RR Value'], tablefmt='grid'))
    
    # Section 3: Butterflies
    print("\n3. BUTTERFLIES")
    print("-" * 40)
    bf_table = []
    for delta in ['25D', '10D']:
        for tenor, value in butterflies[delta].items():
            ticker = f"{pair[:3]}{delta[:-1]}B{tenor}"
            bf_table.append([ticker, f"{delta} {tenor}", f"{value:.3f}"])
    print(tabulate(bf_table, headers=['Bloomberg Ticker', 'Strike/Tenor', 'BF Value'], tablefmt='grid'))
    
    # Section 4: Complete Volatility Smile Grid
    print("\n4. VOLATILITY SMILE GRID (Matching Bloomberg Terminal Format)")
    print("-" * 60)
    smile_grid = calculate_smile_grid(atm_vols, risk_reversals, butterflies)
    headers = ['Tenor', '10Δ Put', '25Δ Put', 'ATM', '25Δ Call', '10Δ Call']
    print(tabulate(smile_grid, headers=headers, tablefmt='grid'))
    
    # Section 5: Surface Characteristics
    print("\n5. SURFACE CHARACTERISTICS")
    print("-" * 40)
    
    # Calculate some key metrics
    rr_1m = risk_reversals['25D'].get('1M', 0)
    rr_1y = risk_reversals['25D'].get('1Y', 0)
    bf_avg = sum(butterflies['25D'].values()) / len(butterflies['25D']) if butterflies['25D'] else 0
    
    characteristics = [
        ["Short-term Skew", "Negative (Put premium)" if rr_1m < 0 else "Positive (Call premium)"],
        ["Long-term Skew", "Negative (Put premium)" if rr_1y < 0 else "Positive (Call premium)"],
        ["Skew Term Structure", "Flipping" if (rr_1m < 0 and rr_1y > 0) else "Consistent"],
        ["Average 25Δ Butterfly", f"{bf_avg:.3f}"],
        ["Smile Convexity", "High" if bf_avg > 0.2 else "Normal"]
    ]
    print(tabulate(characteristics, headers=['Metric', 'Value'], tablefmt='grid'))
    
    # Section 6: Verification Instructions
    print("\n6. BLOOMBERG TERMINAL VERIFICATION")
    print("-" * 40)
    print("To verify this matches your Bloomberg Terminal:")
    print("1. On Terminal, type: EURUSD Curncy OVDV <GO>")
    print("2. Compare ATM vols with Section 1 above")
    print("3. Check RR/BF values in the volatility matrix")
    print("4. Verify smile shape in the 2D smile chart")
    print("5. Compare 3D surface shape and colors")
    
    print("\n" + "=" * 80)
    print("END OF REPORT")

if __name__ == "__main__":
    generate_bloomberg_format_report("EURUSD")