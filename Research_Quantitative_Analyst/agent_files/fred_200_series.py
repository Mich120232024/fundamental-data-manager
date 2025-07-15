#!/usr/bin/env python3
"""
FRED 200 Series Comprehensive Economic Data
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Retrieve 200 key economic series from FRED for comprehensive macroeconomic analysis
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fredapi import Fred
import time

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Initialize FRED client
FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    print("❌ ERROR: FRED_API_KEY not found in environment variables")
    sys.exit(1)

fred = Fred(api_key=FRED_API_KEY)

# Comprehensive list of 200 economic indicators
ECONOMIC_SERIES = {
    # GDP and Components (15)
    'GDP': ['GDPC1', 'GDP', 'GDPPOT', 'NYGDPMKTPCDWLD', 'GDPDEF',
            'PCECC96', 'GPDIC1', 'GCEC1', 'NETEXC', 'DGDSRC1',
            'DNDGRC1', 'DSERGC1', 'A191RL1Q225SBEA', 'GDPC1CTM', 'NGDPPOT'],
    
    # Employment and Labor (20)
    'EMPLOYMENT': ['PAYEMS', 'UNRATE', 'CIVPART', 'EMRATIO', 'UEMPMEAN',
                   'UEMPMED', 'U6RATE', 'NROU', 'ICSA', 'CCSA',
                   'JTSQUL', 'JTSJOL', 'CES0500000003', 'AWHAETP', 'AHETPI',
                   'MANEMP', 'USCONS', 'USTRADE', 'USFIRE', 'USGOVT'],
    
    # Inflation Measures (15)
    'INFLATION': ['CPIAUCSL', 'CPILFESL', 'PCEPI', 'PCEPILFE', 'DFEDTARU',
                  'DFEDTARL', 'CORESTICKM159SFRBATL', 'MEDCPIM158SFRBCLE', 'TRIMAFEM158SFRBCLE', 'BPCCRO1Q156NBEA',
                  'CPIFABSL', 'CPIMEDSL', 'CUSR0000SA0', 'PPIFGS', 'PPIACO'],
    
    # Interest Rates and Yields (20)
    'RATES': ['FEDFUNDS', 'DGS1', 'DGS2', 'DGS5', 'DGS10', 'DGS30',
              'T10Y2Y', 'T10Y3M', 'DFII10', 'TB3MS', 'TB6MS',
              'GS1M', 'GS3M', 'GS6M', 'GS1', 'GS2',
              'GS3', 'GS5', 'GS7', 'GS20'],
    
    # Housing Market (15)
    'HOUSING': ['HOUST', 'PERMITS', 'MSPUS', 'CSUSHPISA', 'MORTGAGE30US',
                'MORTGAGE15US', 'RHORUSQ156N', 'MSACSR', 'HSN1F', 'COMPUTSA',
                'COMREPUSQ159N', 'NHSUSSPT', 'EVACANTUSQ176N', 'RHVRUSQ156N', 'EXHOSLUSM495S'],
    
    # Manufacturing and Production (15)
    'MANUFACTURING': ['INDPRO', 'CAPUTLG2211S', 'MCUMFN', 'IPMAN', 'IPFINAL',
                      'IPCONGD', 'NAPMEI', 'NAPMNOI', 'NAPMSDI', 'NAPMII',
                      'DGORDER', 'NEWORDER', 'BUSINV', 'ISRATIO', 'TOTALSA'],
    
    # Consumer Indicators (15)
    'CONSUMER': ['UMCSENT', 'RSXFS', 'PSAVERT', 'PCEC96', 'DSPIC96',
                 'PCE', 'PCEDG', 'PCEND', 'PCES', 'A229RX0',
                 'TOTALSL', 'CONSUMER', 'DTCOLNVHFNM', 'TDSP', 'REVOLSL'],
    
    # Financial Markets (20)
    'FINANCIAL': ['SP500', 'DJIA', 'NASDAQCOM', 'VIXCLS', 'DEXUSEU',
                  'DEXJPUS', 'DEXCAUS', 'DEXUSUK', 'DEXCHUS', 'DEXMXUS',
                  'DTWEXBGS', 'BAMLH0A0HYM2', 'BAMLC0A0CM', 'TEDRATE', 'DCOILWTICO',
                  'GOLDPMGBD228NLBM', 'DHHNGSP', 'DCOILBRENTEU', 'GASREGW', 'DJCA'],
    
    # Money Supply and Credit (15)
    'MONEY_CREDIT': ['M1SL', 'M2SL', 'BOGMBASE', 'TOTRESNS', 'BUSLOANS',
                     'REALLN', 'NONREVSL', 'CCLACBW027SBOG', 'DRISCFLM', 'DPSACBW027SBOG',
                     'H8B1001NCBCMG', 'TOTBKCR', 'USGSEC', 'OTHSEC', 'INVEST'],
    
    # Trade and International (15)
    'TRADE': ['NETEXP', 'EXPGS', 'IMPGS', 'BOPGSTB', 'IEABC',
              'XTEXVA01USM664S', 'XTIMVA01USM664S', 'USATRADEBALGDPB6PT', 'CURCIR', 'EXUSEU',
              'EXJPUS', 'EXCAUS', 'EXMXUS', 'EXCHUS', 'EXUSUK'],
    
    # Government and Fiscal (15)
    'GOVERNMENT': ['GFDEBTN', 'GFDEGDQ188S', 'FYFSD', 'FYFR', 'FYONET',
                   'W006RC1Q027SBEA', 'A191RC1Q027SBEA', 'GCEC1', 'GEXPND', 'GRECPT',
                   'FGEXPND', 'FGRECPT', 'SLEXPND', 'SLRECPT', 'GFDGDPA188S'],
    
    # Business and Corporate (15)
    'BUSINESS': ['CORPPROFIT', 'CP', 'CPROFIT', 'BCNSDODNS', 'BCFDDODNS',
                 'NCBDBIQ027S', 'TODNS', 'DODFS', 'FBCELLQ027S', 'TNWBSHNO',
                 'BOGZ1FL072051003Q', 'BOGZ1FL073164003Q', 'BOGZ1FL073169175Q', 'TABSHNO', 'NETINC'],
    
    # Regional and State (10)
    'REGIONAL': ['NYSTHPI', 'CASTHPI', 'TXSTHPI', 'FLSTHPI', 'WASTHPI',
                 'NYUR', 'CAUR', 'TXUR', 'FLUR', 'ILUR']
}

def get_200_series():
    """Retrieve 200 economic series from FRED"""
    
    print("🔍 Fetching 200 FRED Economic Series")
    print("="*60)
    
    all_series_data = []
    failed_series = []
    series_count = 0
    
    # Get data from the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for category, series_list in ECONOMIC_SERIES.items():
        print(f"\n📊 Processing {category} indicators...")
        
        for series_id in series_list:
            try:
                # Rate limiting - be nice to FRED API
                time.sleep(0.1)
                
                # Get series info
                info = fred.get_series_info(series_id)
                
                # Get latest data
                data = fred.get_series(series_id, 
                                     observation_start=start_date,
                                     observation_end=end_date)
                
                if data is not None and len(data) > 0:
                    all_series_data.append({
                        'category': category,
                        'series_id': series_id,
                        'series_title': info.get('title', 'Unknown'),
                        'latest_value': data.iloc[-1],
                        'latest_date': data.index[-1],
                        'units': info.get('units', 'Unknown'),
                        'frequency': info.get('frequency', 'Unknown'),
                        'seasonal_adjustment': info.get('seasonal_adjustment', 'Unknown'),
                        'last_updated': info.get('last_updated', 'Unknown'),
                        'popularity': info.get('popularity', 0),
                        'observation_start': info.get('observation_start', 'Unknown'),
                        'observation_end': info.get('observation_end', 'Unknown')
                    })
                    
                    series_count += 1
                    
                    # Progress indicator
                    if series_count % 10 == 0:
                        print(f"   ✓ Processed {series_count} series...")
                    
                else:
                    failed_series.append((series_id, "No data returned"))
                    
            except Exception as e:
                failed_series.append((series_id, str(e)))
                continue
    
    # Create DataFrame
    df = pd.DataFrame(all_series_data)
    
    if not df.empty:
        # Sort by category and latest_date
        df = df.sort_values(['category', 'latest_date'], ascending=[True, False])
        
        print("\n" + "="*60)
        print(f"✅ Successfully loaded {len(df)} series into DataFrame")
        
        if failed_series:
            print(f"\n⚠️  Failed to retrieve {len(failed_series)} series:")
            for series_id, error in failed_series[:5]:  # Show first 5 failures
                print(f"   - {series_id}: {error}")
            if len(failed_series) > 5:
                print(f"   ... and {len(failed_series) - 5} more")
        
        # Save to CSV
        csv_path = 'fred_200_series_data.csv'
        df.to_csv(csv_path, index=False)
        print(f"\n💾 Data saved to: {csv_path}")
        
        # Display summary statistics
        print("\n📊 DataFrame Summary:")
        print(f"   Shape: {df.shape}")
        print(f"   Categories: {df['category'].nunique()}")
        print(f"   Date range: {df['latest_date'].min()} to {df['latest_date'].max()}")
        
        # Category breakdown
        print("\n📈 Series by Category:")
        category_counts = df['category'].value_counts()
        for cat, count in category_counts.items():
            print(f"   {cat}: {count} series")
        
        # Sample of data
        print("\n🔍 Sample Data (5 most recent updates):")
        recent_5 = df.nlargest(5, 'latest_date')[['series_id', 'series_title', 'latest_value', 'latest_date']]
        print(recent_5.to_string(index=False))
        
        return df
    else:
        print("\n❌ Failed to create DataFrame")
        return None

if __name__ == "__main__":
    # Get 200 series
    df = get_200_series()
    
    if df is not None:
        print("\n✅ 200 Series DataFrame Ready for Analysis")
        
        # Additional analysis
        print("\n📊 Quick Analysis:")
        
        # Most frequently updated series
        df['last_updated_parsed'] = pd.to_datetime(df['last_updated'])
        most_recent_updates = df.nlargest(10, 'last_updated_parsed')[['series_id', 'series_title', 'last_updated']]
        print("\n🔄 Most Recently Updated Series:")
        print(most_recent_updates.to_string(index=False))
        
        # High frequency series
        daily_series = df[df['frequency'] == 'Daily']
        print(f"\n📅 Daily Series Count: {len(daily_series)}")
        
        # Create a pivot summary
        pivot_summary = df.pivot_table(index='category', values='series_id', aggfunc='count')
        pivot_summary.to_csv('fred_200_series_summary.csv')
        print("\n💾 Summary saved to: fred_200_series_summary.csv")