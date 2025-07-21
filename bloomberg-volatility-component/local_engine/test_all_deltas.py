#!/usr/bin/env python3
"""
Test retrieval of all delta values (every 5)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.bloomberg_client import BloombergAPIClient
import pandas as pd

def test_all_deltas():
    """Test retrieving all delta values"""
    
    print("Testing Bloomberg API with all delta values (every 5)...")
    client = BloombergAPIClient()
    
    # Check health first
    try:
        health = client.health_check()
        if health.get("success"):
            print("✓ API is healthy")
        else:
            print("✗ API health check failed")
            return
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return
    
    # Test getting all deltas
    print("\nFetching EURUSD 1M volatility surface with all deltas...")
    
    try:
        # Get the full surface
        df = client.get_fx_volatility_surface("EURUSD", "1M")
        
        print(f"\nRetrieved {len(df)} data points")
        
        # Group by product type
        for product in ["ATM", "RR", "BF"]:
            product_df = df[df["Product"] == product]
            print(f"\n{product}:")
            
            if product == "ATM":
                row = product_df.iloc[0]
                print(f"  ATM: {row['Mid']:.3f}% (Bid: {row['Bid']:.3f}%, Ask: {row['Ask']:.3f}%)")
            else:
                for _, row in product_df.iterrows():
                    status = "✓" if row['Mid'] is not None else "✗"
                    if row['Mid'] is not None:
                        print(f"  {status} {row['Delta']}: {row['Mid']:.3f}% (Bid: {row['Bid']:.3f}%, Ask: {row['Ask']:.3f}%)")
                    else:
                        print(f"  {status} {row['Delta']}: No data available")
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY:")
        print(f"Total securities requested: {len(df)}")
        print(f"Successful data points: {len(df[df['Mid'].notna()])}")
        print(f"Missing data points: {len(df[df['Mid'].isna()])}")
        
        # Show which deltas are missing data
        missing = df[df['Mid'].isna()]
        if not missing.empty:
            print("\nMissing data for:")
            for _, row in missing.iterrows():
                print(f"  - {row['Product']} {row['Delta']}")
        
    except Exception as e:
        print(f"\n✗ Error fetching volatility data: {e}")


if __name__ == "__main__":
    test_all_deltas()