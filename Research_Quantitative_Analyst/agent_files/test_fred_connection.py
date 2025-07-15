#!/usr/bin/env python3
"""
Test FRED API Connection
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Verify FRED API connectivity and retrieve sample economic data
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Verify FRED API key is loaded
FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    print("❌ ERROR: FRED_API_KEY not found in environment variables")
    sys.exit(1)

print(f"✅ FRED API Key loaded: {FRED_API_KEY[:8]}...{FRED_API_KEY[-4:]}")

try:
    from fredapi import Fred
    print("✅ fredapi library imported successfully")
except ImportError:
    print("❌ ERROR: fredapi library not installed")
    print("   Please install with: pip install fredapi")
    sys.exit(1)

def test_fred_connection():
    """Test FRED API connection and retrieve sample data"""
    
    print("\n" + "="*60)
    print("🔍 Testing FRED API Connection")
    print("="*60)
    
    try:
        # Initialize FRED API client
        fred = Fred(api_key=FRED_API_KEY)
        print("✅ FRED client initialized successfully")
        
        # Test 1: Get a simple series (GDP)
        print("\n📊 Test 1: Retrieving GDP data (GDPC1)...")
        try:
            # Get last 5 years of quarterly GDP data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365*5)
            
            gdp_data = fred.get_series('GDPC1', 
                                      observation_start=start_date, 
                                      observation_end=end_date)
            
            if gdp_data is not None and len(gdp_data) > 0:
                print(f"✅ Successfully retrieved {len(gdp_data)} GDP observations")
                print(f"   Latest GDP value: ${gdp_data.iloc[-1]:,.2f} billion")
                print(f"   Date: {gdp_data.index[-1].strftime('%Y-%m-%d')}")
            else:
                print("⚠️  No GDP data returned")
        except Exception as e:
            print(f"❌ Error retrieving GDP data: {str(e)}")
        
        # Test 2: Get series info
        print("\n📋 Test 2: Retrieving series metadata...")
        try:
            series_info = fred.get_series_info('GDPC1')
            if series_info is not None:
                print("✅ Successfully retrieved series metadata")
                print(f"   Title: {series_info.get('title', 'N/A')}")
                print(f"   Units: {series_info.get('units', 'N/A')}")
                print(f"   Frequency: {series_info.get('frequency', 'N/A')}")
                print(f"   Last Updated: {series_info.get('last_updated', 'N/A')}")
        except Exception as e:
            print(f"❌ Error retrieving series info: {str(e)}")
        
        # Test 3: Get unemployment rate
        print("\n📈 Test 3: Retrieving Unemployment Rate (UNRATE)...")
        try:
            unemployment = fred.get_series('UNRATE', 
                                         observation_start=datetime.now() - timedelta(days=365),
                                         observation_end=datetime.now())
            
            if unemployment is not None and len(unemployment) > 0:
                print(f"✅ Successfully retrieved {len(unemployment)} unemployment observations")
                print(f"   Latest unemployment rate: {unemployment.iloc[-1]:.1f}%")
                print(f"   Date: {unemployment.index[-1].strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"❌ Error retrieving unemployment data: {str(e)}")
        
        # Test 4: Search for series
        print("\n🔎 Test 4: Searching for inflation-related series...")
        try:
            search_results = fred.search('consumer price index', limit=5)
            if search_results is not None and len(search_results) > 0:
                print(f"✅ Found {len(search_results)} series matching 'consumer price index'")
                print("   Top 3 results:")
                for idx, (series_id, info) in enumerate(search_results.head(3).iterrows()):
                    print(f"   {idx+1}. {series_id}: {info.get('title', 'N/A')}")
        except Exception as e:
            print(f"❌ Error searching series: {str(e)}")
        
        print("\n" + "="*60)
        print("✅ FRED API CONNECTION TEST COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: Failed to initialize FRED client")
        print(f"   Error details: {str(e)}")
        print("\n" + "="*60)
        print("❌ FRED API CONNECTION TEST FAILED")
        print("="*60)
        return False

if __name__ == "__main__":
    # Run the test
    success = test_fred_connection()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)