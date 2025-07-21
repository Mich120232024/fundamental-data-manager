#!/usr/bin/env python3
"""
Display EURUSD Volatility Surface in Bloomberg Style
This script fetches live data from the Bloomberg API and displays it in a table
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.bloomberg_client import BloombergAPIClient
from components.volatility_table import VolatilitySurfaceTable


def main():
    """Display EURUSD volatility surface"""
    
    print("Connecting to Bloomberg API...")
    client = BloombergAPIClient()
    
    # Check if API is healthy
    try:
        health = client.health_check()
        if health.get("data", {}).get("bloomberg_terminal_running"):
            print("✓ Bloomberg Terminal connected")
        else:
            print("✗ Bloomberg Terminal not available")
            return
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return
    
    # Create table display
    table_display = VolatilitySurfaceTable(client)
    
    # Display EURUSD 1M volatility surface
    try:
        print("\nFetching EURUSD 1M volatility surface...")
        
        # Display Bloomberg-style table
        print(table_display.create_bloomberg_style_table("EURUSD", "1M"))
        
        # Display summary with key metrics
        table_display.display_surface_summary("EURUSD", "1M")
        
    except Exception as e:
        print(f"\n✗ Error fetching volatility data: {e}")
        return
    
    # Optional: Save to CSV
    try:
        df = client.get_fx_volatility_surface("EURUSD", "1M")
        df.to_csv("eurusd_1m_volatility_surface.csv", index=False)
        print("\n✓ Data saved to eurusd_1m_volatility_surface.csv")
    except Exception as e:
        print(f"\n✗ Error saving data: {e}")


if __name__ == "__main__":
    main()