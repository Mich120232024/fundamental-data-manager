#!/usr/bin/env python3
"""
Test DataFrame processing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.bloomberg_client import BloombergAPIClient
import pandas as pd

def test_dataframe():
    """Test DataFrame processing"""
    
    client = BloombergAPIClient()
    
    try:
        # Get the full surface
        df = client.get_fx_volatility_surface("EURUSD", "1M")
        
        print("DataFrame info:")
        print(df.info())
        print(f"\nShape: {df.shape}")
        print(f"\nColumns: {df.columns.tolist()}")
        
        print("\nFirst few rows:")
        print(df.head())
        
        print("\nGrouped by Product:")
        print(df.groupby('Product').size())
        
        # Check ATM data
        atm_df = df[df["Product"] == "ATM"]
        print(f"\nATM DataFrame shape: {atm_df.shape}")
        print("ATM data:")
        print(atm_df)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_dataframe()