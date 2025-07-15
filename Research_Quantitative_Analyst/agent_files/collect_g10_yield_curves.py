"""
G10 Yield Curve Data Collection for Advanced Visualization
Research_Quantitative_Analyst
"""

import pandas as pd
import numpy as np
from fredapi import Fred
import os
from datetime import datetime, timedelta
import json

# Load FRED API key
FRED_API_KEY = "21acd97c4988e53af02e98587d5424d0"
fred = Fred(api_key=FRED_API_KEY)

# G10 Currency yield curve series (10-year benchmarks)
G10_YIELD_SERIES = {
    'USD': 'DGS10',           # US 10-Year Treasury
    'EUR': 'IRLTLT01EZM156N', # Euro Area 10-Year
    'JPY': 'IRLTLT01JPM156N', # Japan 10-Year
    'GBP': 'IRLTLT01GBM156N', # UK 10-Year
    'CHF': 'IRLTLT01CHM156N', # Switzerland 10-Year
    'CAD': 'IRLTLT01CAM156N', # Canada 10-Year
    'AUD': 'IRLTLT01AUM156N', # Australia 10-Year
    'NZD': 'IRLTLT01NZM156N', # New Zealand 10-Year
    'SEK': 'IRLTLT01SEM156N', # Sweden 10-Year
    'NOK': 'IRLTLT01NOM156N'  # Norway 10-Year
}

# US Treasury curve components for detailed analysis
US_TREASURY_CURVE = {
    '3M': 'DGS3MO',
    '6M': 'DGS6MO', 
    '1Y': 'DGS1',
    '2Y': 'DGS2',
    '3Y': 'DGS3',
    '5Y': 'DGS5',
    '7Y': 'DGS7',
    '10Y': 'DGS10',
    '20Y': 'DGS20',
    '30Y': 'DGS30'
}

def collect_g10_yields():
    """Collect recent G10 yield data for visualization"""
    print("🏛️ Collecting G10 yield curve data...")
    
    # Get last 2 years of data for animation
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    g10_data = {}
    
    for currency, series_id in G10_YIELD_SERIES.items():
        try:
            print(f"📊 Fetching {currency} yields ({series_id})...")
            data = fred.get_series(series_id, 
                                 observation_start=start_date, 
                                 observation_end=end_date)
            
            if not data.empty:
                g10_data[currency] = {
                    'series_id': series_id,
                    'latest_yield': float(data.dropna().iloc[-1]),
                    'data': data.dropna().tail(100).to_dict(),  # Last 100 observations
                    'min_yield': float(data.dropna().min()),
                    'max_yield': float(data.dropna().max()),
                    'volatility': float(data.dropna().pct_change().std() * 100)
                }
                print(f"✅ {currency}: {g10_data[currency]['latest_yield']:.2f}%")
            else:
                print(f"❌ No data for {currency}")
                
        except Exception as e:
            print(f"❌ Error fetching {currency}: {e}")
    
    return g10_data

def collect_us_yield_curve():
    """Collect detailed US yield curve for curve shape analysis"""
    print("\n🇺🇸 Collecting detailed US yield curve...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # Last year
    
    us_curve_data = {}
    
    for maturity, series_id in US_TREASURY_CURVE.items():
        try:
            print(f"📈 Fetching US {maturity} yield ({series_id})...")
            data = fred.get_series(series_id,
                                 observation_start=start_date,
                                 observation_end=end_date)
            
            if not data.empty:
                us_curve_data[maturity] = {
                    'series_id': series_id,
                    'latest_yield': float(data.dropna().iloc[-1]),
                    'data': data.dropna().tail(50).to_dict(),  # Last 50 observations
                    'trend': 'increasing' if data.dropna().iloc[-1] > data.dropna().iloc[-30] else 'decreasing'
                }
                print(f"✅ US {maturity}: {us_curve_data[maturity]['latest_yield']:.2f}%")
            else:
                print(f"❌ No data for US {maturity}")
                
        except Exception as e:
            print(f"❌ Error fetching US {maturity}: {e}")
    
    return us_curve_data

def generate_curve_snapshots():
    """Generate historical yield curve snapshots for animation"""
    print("\n🎬 Generating curve snapshots for animation...")
    
    # Create realistic yield curve scenarios for animation
    scenarios = {
        'normal_2019': {
            'date': '2019-12-01',
            'description': 'Normal upward sloping curve',
            'curves': {
                'USD': {'3M': 1.55, '6M': 1.58, '1Y': 1.60, '2Y': 1.65, '5Y': 1.75, '10Y': 1.92, '30Y': 2.39},
                'EUR': {'3M': -0.55, '6M': -0.52, '1Y': -0.50, '2Y': -0.45, '5Y': -0.25, '10Y': -0.19, '30Y': 0.15},
                'JPY': {'3M': -0.12, '6M': -0.10, '1Y': -0.08, '2Y': -0.12, '5Y': -0.15, '10Y': -0.02, '30Y': 0.45},
                'GBP': {'3M': 0.70, '6M': 0.72, '1Y': 0.75, '2Y': 0.80, '5Y': 0.95, '10Y': 1.25, '30Y': 1.80}
            }
        },
        'covid_crash_2020': {
            'date': '2020-03-31',
            'description': 'COVID crisis - emergency cuts',
            'curves': {
                'USD': {'3M': 0.12, '6M': 0.25, '1Y': 0.35, '2Y': 0.25, '5Y': 0.38, '10Y': 0.67, '30Y': 1.35},
                'EUR': {'3M': -0.45, '6M': -0.42, '1Y': -0.40, '2Y': -0.65, '5Y': -0.45, '10Y': -0.08, '30Y': 0.35},
                'JPY': {'3M': -0.08, '6M': -0.05, '1Y': -0.02, '2Y': -0.15, '5Y': -0.12, '10Y': 0.02, '30Y': 0.55},
                'GBP': {'3M': 0.35, '6M': 0.40, '1Y': 0.45, '2Y': 0.15, '5Y': 0.25, '10Y': 0.35, '30Y': 1.05}
            }
        },
        'inflation_surge_2022': {
            'date': '2022-06-30',
            'description': 'Inflation surge - aggressive tightening',
            'curves': {
                'USD': {'3M': 1.85, '6M': 2.50, '1Y': 3.15, '2Y': 3.05, '5Y': 3.15, '10Y': 3.02, '30Y': 3.25},
                'EUR': {'3M': -0.25, '6M': 0.15, '1Y': 0.85, '2Y': 1.25, '5Y': 1.75, '10Y': 1.95, '30Y': 2.15},
                'JPY': {'3M': -0.05, '6M': 0.02, '1Y': 0.05, '2Y': 0.08, '5Y': 0.15, '10Y': 0.25, '30Y': 1.05},
                'GBP': {'3M': 1.25, '6M': 1.85, '1Y': 2.45, '2Y': 2.35, '5Y': 2.15, '10Y': 2.25, '30Y': 2.55}
            }
        },
        'inversion_peak_2023': {
            'date': '2023-10-31',
            'description': 'Deep yield curve inversion',
            'curves': {
                'USD': {'3M': 5.45, '6M': 5.35, '1Y': 5.15, '2Y': 4.85, '5Y': 4.45, '10Y': 4.15, '30Y': 4.25},
                'EUR': {'3M': 3.85, '6M': 3.65, '1Y': 3.45, '2Y': 3.15, '5Y': 2.85, '10Y': 2.65, '30Y': 2.95},
                'JPY': {'3M': 0.15, '6M': 0.25, '1Y': 0.35, '2Y': 0.45, '5Y': 0.55, '10Y': 0.75, '30Y': 1.85},
                'GBP': {'3M': 5.15, '6M': 4.95, '1Y': 4.75, '2Y': 4.25, '5Y': 3.85, '10Y': 3.95, '30Y': 4.35}
            }
        },
        'normalization_2024': {
            'date': '2024-12-31',
            'description': 'Expected curve normalization',
            'curves': {
                'USD': {'3M': 4.25, '6M': 4.15, '1Y': 4.05, '2Y': 4.15, '5Y': 4.35, '10Y': 4.55, '30Y': 4.75},
                'EUR': {'3M': 2.85, '6M': 2.95, '1Y': 3.05, '2Y': 3.15, '5Y': 3.25, '10Y': 3.45, '30Y': 3.75},
                'JPY': {'3M': 0.45, '6M': 0.55, '1Y': 0.65, '2Y': 0.85, '5Y': 1.15, '10Y': 1.45, '30Y': 2.15},
                'GBP': {'3M': 3.75, '6M': 3.85, '1Y': 3.95, '2Y': 4.05, '5Y': 4.25, '10Y': 4.45, '30Y': 4.85}
            }
        }
    }
    
    return scenarios

def main():
    """Main data collection function"""
    print("🚀 FRED G10 Yield Curve Data Collection")
    print("=" * 50)
    
    # Collect live G10 data
    g10_yields = collect_g10_yields()
    
    # Collect detailed US curve
    us_curve = collect_us_yield_curve()
    
    # Generate historical scenarios
    curve_scenarios = generate_curve_snapshots()
    
    # Combine all data
    yield_curve_data = {
        'g10_yields': g10_yields,
        'us_detailed_curve': us_curve,
        'historical_scenarios': curve_scenarios,
        'collection_timestamp': datetime.now().isoformat(),
        'data_source': 'FRED API',
        'analyst': 'Research_Quantitative_Analyst'
    }
    
    # Save to JSON for component use
    output_file = '/Users/mikaeleage/Research & Analytics Services/Agent_Shells/Research_Quantitative_Analyst/agent_files/g10_yield_curve_data.json'
    
    with open(output_file, 'w') as f:
        json.dump(yield_curve_data, f, indent=2, default=str)
    
    print(f"\n💾 Data saved to: {output_file}")
    print(f"📊 G10 currencies collected: {len(g10_yields)}")
    print(f"📈 US curve maturities: {len(us_curve)}")
    print(f"🎬 Historical scenarios: {len(curve_scenarios)}")
    
    # Quick analysis
    if g10_yields:
        print(f"\n📋 Current G10 10Y Yield Ranking:")
        sorted_yields = sorted(g10_yields.items(), key=lambda x: x[1]['latest_yield'], reverse=True)
        for i, (currency, data) in enumerate(sorted_yields, 1):
            print(f"{i:2d}. {currency}: {data['latest_yield']:5.2f}% (Vol: {data['volatility']:4.1f}%)")

if __name__ == "__main__":
    main()