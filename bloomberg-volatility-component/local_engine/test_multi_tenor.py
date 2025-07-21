#!/usr/bin/env python3
"""
Test multi-tenor volatility surface
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'api'))

from multi_tenor_client import MultiTenorVolatilityClient
import pandas as pd

# Set display options
pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)

def test_multi_tenor():
    """Test fetching multi-tenor data"""
    
    client = MultiTenorVolatilityClient()
    
    # Test with common tenors
    print("Testing multi-tenor volatility surface...")
    tenors = ["1W", "2W", "1M", "2M", "3M", "6M", "1Y"]
    
    print(f"\nFetching data for tenors: {', '.join(tenors)}")
    df = client.get_multi_tenor_surface("EURUSD", tenors)
    
    # Show Bloomberg-style matrix
    print("\n" + "="*100)
    print("Bloomberg-Style Volatility Matrix (10D and 25D only)")
    print("="*100)
    matrix = client.create_bloomberg_style_matrix(df)
    print(matrix.to_string(index=False, float_format=lambda x: f"{x:7.3f}" if pd.notna(x) else "    -   "))
    
    # Show full delta matrix
    print("\n" + "="*150)
    print("Full Delta Volatility Matrix (All Available Deltas)")
    print("="*150)
    full_matrix = client.create_full_delta_matrix(df)
    print(full_matrix.to_string(index=False, float_format=lambda x: f"{x:7.3f}" if pd.notna(x) else "    -   "))
    
    # Summary
    successful = df[df["success"] == True].shape[0]
    failed = df[df["success"] == False].shape[0]
    
    print(f"\n\nSummary: {successful} successful, {failed} failed")
    
    if failed > 0:
        print("\nFailed tenors:")
        for _, row in df[df["success"] == False].iterrows():
            print(f"  {row['tenor']}: {row.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_multi_tenor()