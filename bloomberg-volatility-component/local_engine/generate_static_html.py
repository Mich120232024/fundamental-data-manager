#!/usr/bin/env python3
"""
Generate static HTML file with volatility data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'api'))

from multi_tenor_client import MultiTenorVolatilityClient
import json

def generate_html():
    """Generate static HTML with embedded data"""
    
    print("Fetching volatility data...")
    client = MultiTenorVolatilityClient()
    
    # Fetch data for EURUSD
    df = client.get_multi_tenor_surface("EURUSD", ["1W", "2W", "1M", "2M", "3M", "6M", "1Y"])
    matrix = client.create_full_delta_matrix(df)
    
    # Convert to JSON-safe format
    data = []
    for _, row in matrix.iterrows():
        row_dict = {}
        for col, val in row.items():
            if pd.isna(val) or val is None:
                row_dict[col] = None
            else:
                row_dict[col] = float(val) if isinstance(val, (int, float)) else val
        data.append(row_dict)
    
    # Generate HTML
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Bloomberg Volatility Surface - EURUSD</title>
    <style>
        body {
            background: #000;
            color: #fff;
            font-family: 'Courier New', monospace;
            margin: 20px;
        }
        h1 {
            color: #ff6600;
            text-align: center;
        }
        .header {
            background: #000;
            border-bottom: 2px solid #ff6600;
            padding: 10px;
            margin-bottom: 20px;
        }
        table {
            border-collapse: collapse;
            margin: 20px auto;
            font-size: 14px;
        }
        th {
            background: #333;
            color: #ff6600;
            padding: 8px;
            border: 1px solid #666;
            text-align: right;
            font-weight: normal;
        }
        th:first-child {
            text-align: left;
            background: #ff6600;
            color: #000;
            font-weight: bold;
        }
        td {
            padding: 6px 10px;
            border: 1px solid #333;
            background: #111;
            text-align: right;
        }
        td:first-child {
            text-align: left;
            background: #ff6600;
            color: #000;
            font-weight: bold;
        }
        .positive { color: #00ff00; }
        .negative { color: #ff0000; }
        .atm { color: #ffff00; }
        .info {
            text-align: center;
            color: #666;
            margin: 20px;
        }
        tr:hover td:not(:first-child) {
            background: #222;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>EURUSD VOLATILITY SURFACE</h1>
    </div>
    
    <table>
        <tr>
            <th>Exp</th>
            <th colspan="3">ATM</th>
            <th colspan="2">5D</th>
            <th colspan="2">10D</th>
            <th colspan="2">15D</th>
            <th colspan="2">25D</th>
            <th colspan="2">35D</th>
        </tr>
        <tr>
            <th></th>
            <th>Bid</th><th>Mid</th><th>Ask</th>
            <th>RR</th><th>BF</th>
            <th>RR</th><th>BF</th>
            <th>RR</th><th>BF</th>
            <th>RR</th><th>BF</th>
            <th>RR</th><th>BF</th>
        </tr>
"""
    
    # Add data rows
    for row in data:
        html += '<tr>'
        html += f'<td>{row["Exp"]}</td>'
        
        # ATM values
        html += f'<td class="atm">{format_value(row["ATM_Bid"])}</td>'
        html += f'<td class="atm">{format_value(row["ATM_Mid"])}</td>'
        html += f'<td class="atm">{format_value(row["ATM_Ask"])}</td>'
        
        # Delta values
        for delta in ['5D', '10D', '15D', '25D', '35D']:
            rr_val = row[f'{delta}_RR']
            bf_val = row[f'{delta}_BF']
            
            # RR with color coding
            if rr_val is None:
                html += '<td>-</td>'
            else:
                if rr_val > 0:
                    html += f'<td class="positive">{rr_val:.3f}</td>'
                elif rr_val < 0:
                    html += f'<td class="negative">{rr_val:.3f}</td>'
                else:
                    html += f'<td>{rr_val:.3f}</td>'
            
            # BF
            html += f'<td>{format_value(bf_val)}</td>'
        
        html += '</tr>'
    
    html += """
    </table>
    
    <div class="info">
        <p>Data from Bloomberg Terminal API - Real-time FX Option Volatilities</p>
        <p>RR = Risk Reversal, BF = Butterfly</p>
        <p>All values in implied volatility %</p>
    </div>
</body>
</html>
"""
    
    # Save file
    filename = "bloomberg_volatility_surface.html"
    with open(filename, 'w') as f:
        f.write(html)
    
    print(f"\nStatic HTML file generated: {filename}")
    print(f"Full path: {os.path.abspath(filename)}")
    print("\nYou can open this file directly in Safari!")

def format_value(val):
    """Format value for display"""
    if val is None:
        return '-'
    return f'{val:.3f}'

if __name__ == '__main__':
    import pandas as pd
    generate_html()