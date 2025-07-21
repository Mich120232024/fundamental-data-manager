#!/usr/bin/env python3
"""
Display the volatility surface DataFrame with formatting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.bloomberg_client import BloombergAPIClient
import pandas as pd

# Set pandas display options
pd.set_option('display.width', 120)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.4f}'.format)

def show_dataframe():
    """Display the volatility surface DataFrame"""
    
    client = BloombergAPIClient()
    
    # Get volatility surface
    df = client.get_fx_volatility_surface("EURUSD", "1M")
    
    print("\nEURUSD 1M Volatility Surface DataFrame")
    print("=" * 80)
    print(df.to_string(index=False))
    
    print("\n\nDataFrame Info:")
    print("-" * 40)
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    print("\n\nSummary Statistics:")
    print("-" * 40)
    print(df[['Mid', 'Bid', 'Ask', 'Spread']].describe())
    
    print("\n\nGrouped by Product:")
    print("-" * 40)
    for product in ['ATM', 'RR', 'BF']:
        product_df = df[df['Product'] == product]
        print(f"\n{product}:")
        print(product_df[['Delta', 'Mid', 'Bid', 'Ask', 'Spread']].to_string(index=False))


if __name__ == "__main__":
    show_dataframe()