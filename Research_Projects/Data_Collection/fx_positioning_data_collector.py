#!/usr/bin/env python3
"""
Free FX Positioning Data Collector
Demonstrates automated collection and analysis of free FX positioning data sources.
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time

class FXPositioningCollector:
    """Collects FX positioning data from multiple free sources."""
    
    def __init__(self):
        self.cftc_base_url = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
        self.fx_currencies = {
            'EUR': 'EUROPEAN CURRENCY UNIT',
            'GBP': 'POUND STERLING', 
            'JPY': 'JAPANESE YEN',
            'CHF': 'SWISS FRANC',
            'CAD': 'CANADIAN DOLLAR',
            'AUD': 'AUSTRALIAN DOLLAR'
        }
        
    def get_cftc_positioning(self, currency_code=None, limit=10):
        """
        Fetch CFTC COT positioning data for FX currencies.
        
        Args:
            currency_code (str): Currency code (EUR, GBP, etc.) or None for all
            limit (int): Number of records to fetch
            
        Returns:
            pandas.DataFrame: COT positioning data
        """
        try:
            if currency_code:
                if currency_code not in self.fx_currencies:
                    raise ValueError(f"Currency {currency_code} not supported")
                
                commodity_name = self.fx_currencies[currency_code]
                params = {
                    "$where": f"commodity_name='{commodity_name}'",
                    "$order": "report_date_as_yyyy_mm_dd DESC",
                    "$limit": limit
                }
            else:
                # Get all FX currencies
                params = {
                    "$where": "commodity_subgroup_name='CURRENCY'",
                    "$order": "report_date_as_yyyy_mm_dd DESC", 
                    "$limit": limit * 6  # 6 currencies
                }
            
            response = requests.get(self.cftc_base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                print(f"No data returned for currency: {currency_code}")
                return pd.DataFrame()
                
            df = pd.DataFrame(data)
            
            # Clean and format data
            df['report_date'] = pd.to_datetime(df['report_date_as_yyyy_mm_dd'])
            df['currency'] = df['commodity_name'].map({v: k for k, v in self.fx_currencies.items()})
            
            # Convert positioning columns to numeric
            position_cols = [
                'noncomm_positions_long_all', 'noncomm_positions_short_all',
                'comm_positions_long_all', 'comm_positions_short_all',
                'open_interest_all'
            ]
            
            for col in position_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calculate net positions
            df['noncomm_net'] = df['noncomm_positions_long_all'] - df['noncomm_positions_short_all']
            df['comm_net'] = df['comm_positions_long_all'] - df['comm_positions_short_all']
            
            # Select key columns
            key_columns = [
                'report_date', 'currency', 'commodity_name',
                'noncomm_positions_long_all', 'noncomm_positions_short_all', 'noncomm_net',
                'comm_positions_long_all', 'comm_positions_short_all', 'comm_net',
                'open_interest_all'
            ]
            
            return df[key_columns].copy()
            
        except requests.RequestException as e:
            print(f"Error fetching CFTC data: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error processing CFTC data: {e}")
            return pd.DataFrame()
    
    def analyze_positioning_extremes(self, df, lookback_weeks=52):
        """
        Analyze positioning extremes for contrarian signals.
        
        Args:
            df (pandas.DataFrame): COT positioning data
            lookback_weeks (int): Number of weeks for percentile calculation
            
        Returns:
            pandas.DataFrame: Analysis with percentile rankings
        """
        if df.empty:
            return df
            
        analysis = []
        
        for currency in df['currency'].unique():
            if pd.isna(currency):
                continue
                
            curr_data = df[df['currency'] == currency].copy()
            curr_data = curr_data.sort_values('report_date').tail(lookback_weeks)
            
            if len(curr_data) < 10:  # Need minimum data points
                continue
                
            latest = curr_data.iloc[-1]
            
            # Calculate percentiles for latest positioning
            noncomm_net_pct = (curr_data['noncomm_net'] <= latest['noncomm_net']).mean() * 100
            comm_net_pct = (curr_data['comm_net'] <= latest['comm_net']).mean() * 100
            
            # Determine positioning signals
            if noncomm_net_pct >= 90:
                noncomm_signal = "EXTREME_LONG"
            elif noncomm_net_pct <= 10:
                noncomm_signal = "EXTREME_SHORT"
            elif noncomm_net_pct >= 75:
                noncomm_signal = "BULLISH"
            elif noncomm_net_pct <= 25:
                noncomm_signal = "BEARISH"
            else:
                noncomm_signal = "NEUTRAL"
            
            analysis.append({
                'currency': currency,
                'report_date': latest['report_date'],
                'noncomm_net': latest['noncomm_net'],
                'noncomm_net_percentile': round(noncomm_net_pct, 1),
                'noncomm_signal': noncomm_signal,
                'comm_net': latest['comm_net'],
                'comm_net_percentile': round(comm_net_pct, 1),
                'open_interest': latest['open_interest_all']
            })
        
        return pd.DataFrame(analysis)
    
    def get_positioning_summary(self):
        """Get current positioning summary for all FX currencies."""
        print("Fetching CFTC COT positioning data...")
        
        # Get latest data for all currencies
        df = self.get_cftc_positioning(limit=5)
        
        if df.empty:
            print("No positioning data available")
            return None
            
        # Get most recent date data
        latest_date = df['report_date'].max()
        latest_data = df[df['report_date'] == latest_date]
        
        print(f"\nCFTC COT Positioning Summary - Week of {latest_date.strftime('%Y-%m-%d')}")
        print("=" * 80)
        
        for _, row in latest_data.iterrows():
            currency = row['currency']
            if pd.isna(currency):
                continue
                
            print(f"\n{currency} ({row['commodity_name']}):")
            print(f"  Non-Commercial (Speculators):")
            print(f"    Long: {row['noncomm_positions_long_all']:,}")
            print(f"    Short: {row['noncomm_positions_short_all']:,}")
            print(f"    Net: {row['noncomm_net']:,}")
            
            print(f"  Commercial (Hedgers):")
            print(f"    Long: {row['comm_positions_long_all']:,}")
            print(f"    Short: {row['comm_positions_short_all']:,}")
            print(f"    Net: {row['comm_net']:,}")
            
            print(f"  Open Interest: {row['open_interest_all']:,}")
        
        # Analyze extremes
        print("\n" + "=" * 80)
        print("POSITIONING EXTREMES ANALYSIS (52-week lookback)")
        print("=" * 80)
        
        historical_df = self.get_cftc_positioning(limit=60)  # ~1 year of data
        extremes = self.analyze_positioning_extremes(historical_df)
        
        if not extremes.empty:
            for _, row in extremes.iterrows():
                signal_color = "🔴" if "EXTREME" in row['noncomm_signal'] else "🟡" if row['noncomm_signal'] in ['BULLISH', 'BEARISH'] else "🟢"
                print(f"\n{signal_color} {row['currency']}:")
                print(f"  Speculative Net: {row['noncomm_net']:,} ({row['noncomm_net_percentile']}th percentile)")
                print(f"  Signal: {row['noncomm_signal']}")
                
                if "EXTREME" in row['noncomm_signal']:
                    print(f"  ⚠️  CONTRARIAN OPPORTUNITY: Speculators at {row['noncomm_net_percentile']}th percentile")
        
        return latest_data, extremes

def main():
    """Main execution function."""
    print("Free FX Positioning Data Collector")
    print("==================================")
    
    collector = FXPositioningCollector()
    
    try:
        # Get positioning summary
        result = collector.get_positioning_summary()
        
        if result:
            latest_data, extremes = result
            
            print(f"\n\nDATA SOURCES SUMMARY:")
            print("=" * 50)
            print("✅ CFTC COT Reports: Weekly FX futures positioning")
            print("✅ Free APIs: No authentication or limits")
            print("✅ Historical Data: Back to 1986")
            print("✅ Update Schedule: Every Friday 3:30 PM ET")
            
            print(f"\nNEXT STEPS:")
            print("- Set up automated weekly data collection")
            print("- Integrate Treasury TIC flow data") 
            print("- Add central bank intervention monitoring")
            print("- Develop positioning-based trading signals")
            
        else:
            print("Failed to retrieve positioning data")
            
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main() 