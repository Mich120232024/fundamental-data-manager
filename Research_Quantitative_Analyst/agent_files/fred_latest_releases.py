#!/usr/bin/env python3
"""
FRED Latest Series Updates Analysis
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Retrieve the latest 25 series updates from FRED release schedule
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fredapi import Fred
import json

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Initialize FRED client
FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    print("❌ ERROR: FRED_API_KEY not found in environment variables")
    sys.exit(1)

fred = Fred(api_key=FRED_API_KEY)

def get_latest_releases():
    """Get the latest 25 series updates from FRED"""
    
    print("🔍 Fetching Latest FRED Series Updates")
    print("="*60)
    
    try:
        # Get releases from the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Get all releases
        print("📅 Fetching recent releases...")
        releases = fred.get_all_releases()
        
        if releases is None or releases.empty:
            print("⚠️  No releases data returned")
            return None
            
        # Sort by realtime_start (most recent first)
        releases_sorted = releases.sort_values('realtime_start', ascending=False)
        
        # Get top 25 most recent releases
        recent_releases = releases_sorted.head(25)
        
        print(f"✅ Found {len(releases)} total releases")
        print(f"📊 Processing top 25 most recent releases...")
        
        # Create a list to store series data
        series_data = []
        
        # For each release, get its series
        for idx, (release_id, release_info) in enumerate(recent_releases.iterrows()):
            try:
                print(f"\n📋 Release {idx+1}/25: {release_info.get('name', 'Unknown')}")
                
                # Get series for this release
                release_series = fred.get_release_series(release_id, limit=5)  # Get top 5 series per release
                
                if release_series is not None and not release_series.empty:
                    for series_id, series_info in release_series.iterrows():
                        try:
                            # Get the latest observation for this series
                            series_data_points = fred.get_series(series_id, 
                                                                observation_start=end_date - timedelta(days=90),
                                                                observation_end=end_date)
                            
                            if series_data_points is not None and len(series_data_points) > 0:
                                latest_value = series_data_points.iloc[-1]
                                latest_date = series_data_points.index[-1]
                                
                                series_data.append({
                                    'release_id': release_id,
                                    'release_name': release_info.get('name', 'Unknown'),
                                    'series_id': series_id,
                                    'series_title': series_info.get('title', 'Unknown'),
                                    'latest_value': latest_value,
                                    'latest_date': latest_date,
                                    'units': series_info.get('units', 'Unknown'),
                                    'frequency': series_info.get('frequency', 'Unknown'),
                                    'last_updated': series_info.get('last_updated', 'Unknown')
                                })
                                
                                print(f"   ✓ {series_id}: {latest_value} ({latest_date.strftime('%Y-%m-%d')})")
                                
                        except Exception as e:
                            print(f"   ⚠️  Error processing series {series_id}: {str(e)}")
                            continue
                            
            except Exception as e:
                print(f"   ❌ Error processing release {release_id}: {str(e)}")
                continue
                
            # Limit to 25 series total
            if len(series_data) >= 25:
                break
        
        # Create DataFrame
        df = pd.DataFrame(series_data)
        
        if not df.empty:
            # Sort by latest_date descending
            df = df.sort_values('latest_date', ascending=False)
            
            print("\n" + "="*60)
            print(f"✅ Successfully loaded {len(df)} series into DataFrame")
            print("\n📊 DataFrame Summary:")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {', '.join(df.columns)}")
            print(f"\n📈 Top 5 Most Recent Updates:")
            print(df[['series_id', 'series_title', 'latest_value', 'latest_date']].head())
            
            # Save to CSV for reference
            csv_path = 'fred_latest_25_series.csv'
            df.to_csv(csv_path, index=False)
            print(f"\n💾 Data saved to: {csv_path}")
            
            return df
        else:
            print("⚠️  No series data collected")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching releases: {str(e)}")
        # Alternative approach: Get series updates directly
        print("\n🔄 Trying alternative approach: Recent series updates...")
        return get_alternative_latest_series()

def get_alternative_latest_series():
    """Alternative method: Get recently updated popular series"""
    
    # List of important economic indicators
    key_series = [
        'GDPC1',      # Real GDP
        'UNRATE',     # Unemployment Rate
        'CPIAUCSL',   # CPI
        'FEDFUNDS',   # Federal Funds Rate
        'DGS10',      # 10-Year Treasury Rate
        'DEXUSEU',    # USD/EUR Exchange Rate
        'PAYEMS',     # Nonfarm Payrolls
        'INDPRO',     # Industrial Production
        'HOUST',      # Housing Starts
        'UMCSENT',    # Consumer Sentiment
        'DFEDTARU',   # Fed Funds Target Rate - Upper
        'DFEDTARL',   # Fed Funds Target Rate - Lower
        'MORTGAGE30US', # 30-Year Mortgage Rate
        'DCOILWTICO', # WTI Oil Price
        'GOLDAMGBD228NLBM', # Gold Price
        'NASDAQCOM',  # NASDAQ Composite
        'SP500',      # S&P 500
        'DJIA',       # Dow Jones
        'VIXCLS',     # VIX
        'BAMLH0A0HYM2', # High Yield Spread
        'T10Y2Y',     # 10Y-2Y Yield Spread
        'ICSA',       # Initial Claims
        'RSXFS',      # Retail Sales
        'PCEPILFE',   # Core PCE
        'M2SL'        # M2 Money Supply
    ]
    
    series_data = []
    
    for series_id in key_series:
        try:
            # Get series info
            info = fred.get_series_info(series_id)
            
            # Get latest data
            data = fred.get_series(series_id, 
                                 observation_start=datetime.now() - timedelta(days=90))
            
            if data is not None and len(data) > 0:
                series_data.append({
                    'series_id': series_id,
                    'series_title': info.get('title', 'Unknown'),
                    'latest_value': data.iloc[-1],
                    'latest_date': data.index[-1],
                    'units': info.get('units', 'Unknown'),
                    'frequency': info.get('frequency', 'Unknown'),
                    'last_updated': info.get('last_updated', 'Unknown')
                })
                
                print(f"✓ {series_id}: {data.iloc[-1]} ({data.index[-1].strftime('%Y-%m-%d')})")
                
        except Exception as e:
            print(f"⚠️  Error with {series_id}: {str(e)}")
            continue
    
    df = pd.DataFrame(series_data)
    
    if not df.empty:
        # Sort by last_updated
        df = df.sort_values('latest_date', ascending=False)
        
        # Save to CSV
        csv_path = 'fred_key_indicators_latest.csv'
        df.to_csv(csv_path, index=False)
        print(f"\n💾 Key indicators saved to: {csv_path}")
        
    return df

if __name__ == "__main__":
    # Get latest releases
    df = get_latest_releases()
    
    if df is not None:
        print("\n✅ DataFrame successfully created with latest FRED series updates")
        print(f"\n📊 Quick Statistics:")
        print(f"   Total series: {len(df)}")
        print(f"   Date range: {df['latest_date'].min()} to {df['latest_date'].max()}")
        print(f"   Unique releases: {df['release_name'].nunique() if 'release_name' in df.columns else 'N/A'}")
    else:
        print("\n❌ Failed to create DataFrame")