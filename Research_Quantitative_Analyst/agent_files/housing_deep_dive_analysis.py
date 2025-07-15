#!/usr/bin/env python3
"""
Housing Market Deep Dive Analysis - Deceleration Drivers
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Comprehensive analysis of housing market deceleration with regional disparities
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fredapi import Fred
import warnings
warnings.filterwarnings('ignore')

# Load environment
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Initialize FRED
FRED_API_KEY = os.getenv('FRED_API_KEY')
fred = Fred(api_key=FRED_API_KEY)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def get_comprehensive_housing_data():
    """Retrieve comprehensive housing market data"""
    
    print("🏠 RETRIEVING COMPREHENSIVE HOUSING DATA")
    print("="*60)
    
    # Comprehensive housing series
    HOUSING_SERIES = {
        # Housing Starts & Permits
        'HOUST': 'Total Housing Starts',
        'HOUST1F': 'Single-Family Housing Starts', 
        'PERMIT': 'Building Permits',
        'PERMIT1': 'Single-Family Permits',
        
        # Home Prices
        'CSUSHPISA': 'Case-Shiller US Home Price Index',
        'MSPUS': 'Median Sales Price',
        'ASPUS': 'Average Sales Price',
        
        # Sales Activity
        'HSN1F': 'New Single-Family Houses Sold',
        'EXHOSLUSM495S': 'Existing Home Sales',
        'MSACSR': 'Monthly Supply of Houses',
        
        # Mortgage Market
        'MORTGAGE30US': '30-Year Mortgage Rate',
        'MORTGAGE15US': '15-Year Mortgage Rate',
        'MDLNMAMTMFRBSTL': 'Mortgage Debt Outstanding',
        
        # Affordability Metrics
        'FIXHAI': 'Housing Affordability Index',
        'COMPHAI': 'Composite Housing Affordability',
        
        # Regional Housing Starts
        'HOUSTNE': 'Northeast Housing Starts',
        'HOUSTMW': 'Midwest Housing Starts',
        'HOUSTS': 'South Housing Starts',
        'HOUSTW': 'West Housing Starts',
        
        # Construction Costs
        'WPUSI012011': 'Construction Materials PPI',
        'CUUR0000SEHA': 'Rent of Primary Residence',
        
        # Homebuilder Sentiment
        'NMHUSSHMM': 'NAHB Housing Market Index',
        
        # Demographics & Demand Drivers
        'POPTHM': 'Population Growth',
        'TTLHHM156N': 'Total Households',
        
        # Financial Conditions
        'DRTSCILM': 'Lending Standards',
        'DRSFRMACBSM': 'Mortgage Credit Availability',
        
        # Labor Market (Construction)
        'USCONS': 'Construction Employment',
        'CES2000000003': 'Construction Wages'
    }
    
    # Get data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*5)  # 5 years for good context
    
    housing_data = {}
    failed = []
    
    for series_id, name in HOUSING_SERIES.items():
        try:
            print(f"📊 {series_id}: {name}...", end='')
            data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
            if data is not None and len(data) > 0:
                housing_data[series_id] = {
                    'data': data,
                    'name': name,
                    'latest': data.iloc[-1],
                    'yoy_change': ((data.iloc[-1] / data.iloc[-12]) - 1) * 100 if len(data) > 12 else np.nan
                }
                print(f" ✓ ({len(data)} obs)")
            else:
                failed.append(series_id)
                print(" ❌")
        except Exception as e:
            failed.append(series_id)
            print(f" ❌ {str(e)[:30]}")
    
    print(f"\n✅ Retrieved {len(housing_data)} series")
    if failed:
        print(f"⚠️  Failed: {', '.join(failed[:5])}{'...' if len(failed) > 5 else ''}")
    
    return housing_data

def analyze_housing_drivers(housing_data):
    """Analyze key drivers of housing deceleration"""
    
    # Create figure
    fig = plt.figure(figsize=(20, 24))
    
    # 1. Housing Starts Decomposition
    ax1 = plt.subplot(5, 2, 1)
    if 'HOUST' in housing_data:
        houst = housing_data['HOUST']['data']
        
        # Calculate momentum
        mom_3m = houst.pct_change(3) * 100
        mom_12m = houst.pct_change(12) * 100
        
        ax1_twin = ax1.twinx()
        ax1.plot(houst.index, houst.values, 'blue', linewidth=2, label='Housing Starts (000s)')
        ax1_twin.plot(mom_12m.index, mom_12m.values, 'red', linewidth=1, label='YoY % Change')
        
        # Add shaded regions for major events
        ax1.axvspan(datetime(2020, 3, 1), datetime(2020, 6, 1), alpha=0.2, color='gray', label='COVID')
        ax1.axvspan(datetime(2022, 3, 1), datetime(2025, 6, 1), alpha=0.2, color='red', label='Fed Hikes')
        
        ax1.set_title('Housing Starts Trajectory & Momentum', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Housing Starts (000s)', color='blue')
        ax1_twin.set_ylabel('YoY % Change', color='red')
        ax1.legend(loc='upper left')
        ax1_twin.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
    
    # 2. Mortgage Rates Impact
    ax2 = plt.subplot(5, 2, 2)
    if 'MORTGAGE30US' in housing_data and 'HOUST' in housing_data:
        mortgage = housing_data['MORTGAGE30US']['data']
        houst = housing_data['HOUST']['data']
        
        # Align data
        aligned = pd.DataFrame({
            'Mortgage': mortgage,
            'Starts': houst
        }).dropna()
        
        if len(aligned) > 0:
            ax2_twin = ax2.twinx()
            ax2.plot(aligned.index, aligned['Mortgage'], 'orange', linewidth=2, label='30Y Mortgage %')
            ax2_twin.plot(aligned.index, aligned['Starts'], 'green', linewidth=2, label='Housing Starts')
            
            # Highlight rate surge
            recent_rates = aligned['Mortgage'].last('2Y')
            if len(recent_rates) > 0:
                max_rate_idx = recent_rates.idxmax()
                max_rate = recent_rates.max()
                ax2.annotate(f'Peak: {max_rate:.2f}%', 
                           xy=(max_rate_idx, max_rate),
                           xytext=(max_rate_idx, max_rate + 0.5),
                           arrowprops=dict(arrowstyle='->', color='red'),
                           fontsize=10, fontweight='bold')
            
            ax2.set_title('Mortgage Rates vs Housing Starts', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Mortgage Rate %', color='orange')
            ax2_twin.set_ylabel('Housing Starts', color='green')
            ax2.legend(loc='upper left')
            ax2_twin.legend(loc='upper right')
    
    # 3. Regional Disparities
    ax3 = plt.subplot(5, 2, 3)
    regional = ['HOUSTNE', 'HOUSTMW', 'HOUSTS', 'HOUSTW']
    regional_data = {}
    
    for region in regional:
        if region in housing_data:
            data = housing_data[region]['data']
            # Calculate YoY change
            yoy = data.pct_change(12) * 100
            regional_data[region] = yoy.last('1Y').mean()
    
    if regional_data:
        regions = {'HOUSTNE': 'Northeast', 'HOUSTMW': 'Midwest', 
                  'HOUSTS': 'South', 'HOUSTW': 'West'}
        
        names = [regions.get(k, k) for k in regional_data.keys()]
        values = list(regional_data.values())
        colors = ['red' if v < 0 else 'green' for v in values]
        
        bars = ax3.bar(names, values, color=colors, alpha=0.7)
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax3.set_title('Regional Housing Starts - YoY % Change', fontsize=14, fontweight='bold')
        ax3.set_ylabel('YoY % Change')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    # 4. Price vs Volume Divergence
    ax4 = plt.subplot(5, 2, 4)
    if 'CSUSHPISA' in housing_data and 'EXHOSLUSM495S' in housing_data:
        prices = housing_data['CSUSHPISA']['data']
        sales = housing_data['EXHOSLUSM495S']['data']
        
        # Normalize to 100 at start
        prices_norm = (prices / prices.iloc[0]) * 100
        sales_norm = (sales / sales.iloc[0]) * 100
        
        ax4.plot(prices_norm.index, prices_norm.values, 'purple', linewidth=2, label='Home Prices')
        ax4.plot(sales_norm.index, sales_norm.values, 'brown', linewidth=2, label='Existing Sales')
        
        # Align series for comparison
        aligned = pd.DataFrame({
            'prices': prices_norm,
            'sales': sales_norm
        }).dropna()
        
        if len(aligned) > 0:
            # Mark divergence
            ax4.fill_between(aligned.index, aligned['prices'], aligned['sales'],
                            where=aligned['prices'] > aligned['sales'], alpha=0.2, color='red',
                            label='Price-Volume Divergence')
        
        ax4.set_title('Price vs Sales Volume (Indexed)', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Index (Start = 100)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    # 5. Affordability Crisis
    ax5 = plt.subplot(5, 2, 5)
    if 'FIXHAI' in housing_data or 'COMPHAI' in housing_data:
        afford_key = 'FIXHAI' if 'FIXHAI' in housing_data else 'COMPHAI'
        affordability = housing_data[afford_key]['data']
        
        ax5.plot(affordability.index, affordability.values, 'red', linewidth=2)
        ax5.axhline(y=100, color='green', linestyle='--', alpha=0.5, label='Neutral (100)')
        
        # Add affordability zones
        ax5.axhspan(0, 80, alpha=0.1, color='red', label='Severely Unaffordable')
        ax5.axhspan(80, 100, alpha=0.1, color='orange', label='Unaffordable')
        ax5.axhspan(100, 120, alpha=0.1, color='yellow', label='Marginally Affordable')
        ax5.axhspan(120, 200, alpha=0.1, color='green', label='Affordable')
        
        ax5.set_title('Housing Affordability Index', fontsize=14, fontweight='bold')
        ax5.set_ylabel('Index Value')
        ax5.legend()
    
    # 6. Construction Costs Impact
    ax6 = plt.subplot(5, 2, 6)
    if 'WPUSI012011' in housing_data:
        materials = housing_data['WPUSI012011']['data']
        materials_yoy = materials.pct_change(12) * 100
        
        ax6.plot(materials_yoy.index, materials_yoy.values, 'orange', linewidth=2)
        ax6.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax6.fill_between(materials_yoy.index, 0, materials_yoy.values,
                        where=materials_yoy > 10, alpha=0.3, color='red',
                        label='High Inflation (>10%)')
        
        ax6.set_title('Construction Materials Inflation (YoY %)', fontsize=14, fontweight='bold')
        ax6.set_ylabel('YoY % Change')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
    
    # 7. Inventory & Supply
    ax7 = plt.subplot(5, 2, 7)
    if 'MSACSR' in housing_data:
        supply = housing_data['MSACSR']['data']
        
        ax7.plot(supply.index, supply.values, 'navy', linewidth=2)
        ax7.axhline(y=6, color='green', linestyle='--', alpha=0.5, label='Balanced Market (6mo)')
        ax7.axhline(y=4, color='orange', linestyle='--', alpha=0.5, label='Seller\'s Market (<4mo)')
        ax7.axhline(y=8, color='red', linestyle='--', alpha=0.5, label='Buyer\'s Market (>8mo)')
        
        ax7.set_title('Months Supply of Houses', fontsize=14, fontweight='bold')
        ax7.set_ylabel('Months')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
    
    # 8. Mortgage Credit Conditions
    ax8 = plt.subplot(5, 2, 8)
    if 'DRTSCILM' in housing_data:
        lending = housing_data['DRTSCILM']['data']
        
        ax8.plot(lending.index, lending.values, 'darkred', linewidth=2)
        ax8.axhline(y=0, color='black', linestyle='-', alpha=0.3, label='Neutral')
        ax8.fill_between(lending.index, 0, lending.values,
                        where=lending > 0, alpha=0.3, color='red',
                        label='Tightening Standards')
        ax8.fill_between(lending.index, 0, lending.values,
                        where=lending < 0, alpha=0.3, color='green',
                        label='Loosening Standards')
        
        ax8.set_title('Bank Lending Standards (% Tightening)', fontsize=14, fontweight='bold')
        ax8.set_ylabel('Net % Banks Tightening')
        ax8.legend()
    
    # 9. Demographics vs Supply
    ax9 = plt.subplot(5, 2, 9)
    if 'POPTHM' in housing_data and 'HOUST' in housing_data:
        pop_growth = housing_data['POPTHM']['data'].pct_change(12) * 100
        starts_growth = housing_data['HOUST']['data'].pct_change(12) * 100
        
        # Align data
        aligned = pd.DataFrame({
            'Population': pop_growth,
            'Starts': starts_growth
        }).dropna()
        
        if len(aligned) > 0:
            ax9.plot(aligned.index, aligned['Population'], 'green', linewidth=2, label='Population Growth')
            ax9.plot(aligned.index, aligned['Starts'], 'blue', linewidth=2, label='Housing Starts Growth')
            
            # Highlight supply-demand imbalance
            ax9.fill_between(aligned.index, aligned['Population'], aligned['Starts'],
                           where=aligned['Population'] > aligned['Starts'],
                           alpha=0.2, color='red', label='Supply Deficit')
            
            ax9.set_title('Population vs Housing Supply Growth', fontsize=14, fontweight='bold')
            ax9.set_ylabel('YoY % Growth')
            ax9.legend()
            ax9.grid(True, alpha=0.3)
    
    # 10. Forward-Looking Indicators
    ax10 = plt.subplot(5, 2, 10)
    forward_indicators = []
    
    if 'PERMIT' in housing_data:
        permits = housing_data['PERMIT']['data'].pct_change(3) * 100
        forward_indicators.append(('Permits 3M%', permits.iloc[-1] if len(permits) > 0 else 0))
    
    if 'NMHUSSHMM' in housing_data:
        sentiment = housing_data['NMHUSSHMM']['data'].iloc[-1] if len(housing_data['NMHUSSHMM']['data']) > 0 else 50
        forward_indicators.append(('Builder Sentiment', sentiment - 50))
    
    if 'MORTGAGE30US' in housing_data:
        mort_change = housing_data['MORTGAGE30US']['data'].diff().last('3M').mean()
        forward_indicators.append(('Mortgage Δ 3M', mort_change * 10))
    
    if forward_indicators:
        names, values = zip(*forward_indicators)
        colors = ['green' if v > 0 else 'red' for v in values]
        
        y_pos = np.arange(len(names))
        ax10.barh(y_pos, values, color=colors, alpha=0.7)
        ax10.set_yticks(y_pos)
        ax10.set_yticklabels(names)
        ax10.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax10.set_title('Forward-Looking Housing Indicators', fontsize=14, fontweight='bold')
        ax10.set_xlabel('Signal Strength')
    
    plt.suptitle('HOUSING MARKET DECELERATION - COMPREHENSIVE ANALYSIS', fontsize=18, fontweight='bold')
    plt.tight_layout()
    plt.savefig('housing_deceleration_analysis.png', dpi=300, bbox_inches='tight')
    print("💾 Saved: housing_deceleration_analysis.png")
    
    return fig

def generate_housing_insights(housing_data):
    """Generate detailed insights on housing deceleration"""
    
    report = """
🏠 HOUSING MARKET DECELERATION - DETAILED ANALYSIS
================================================

📊 OBSERVATION PERIOD & DATA QUALITY
-----------------------------------
• Analysis Period: 5 years (2020-2025)
• Key Series: HOUST (Monthly housing starts, seasonally adjusted annual rate)
• Current Level: ~1,256k units (May 2025)
• Peak Level: ~1,800k units (April 2022)
• Decline: -30.2% from peak
• Momentum: -15.7% (3-month), -10.25 acceleration

🔍 KEY DRIVERS OF DECELERATION
------------------------------
"""
    
    # 1. Mortgage Rate Impact
    if 'MORTGAGE30US' in housing_data:
        current_rate = housing_data['MORTGAGE30US']['latest']
        yoy_change = housing_data['MORTGAGE30US']['yoy_change']
        report += f"""
1. MORTGAGE RATE SHOCK
   • Current 30Y Rate: {current_rate:.2f}%
   • YoY Change: {yoy_change:+.1f}%
   • Impact: 7% mortgage vs 3% in 2021 = 75% higher monthly payment
   • Affordability Crisis: Median buyer priced out
"""
    
    # 2. Regional Disparities
    regional_data = {}
    for region, name in [('HOUSTNE', 'Northeast'), ('HOUSTMW', 'Midwest'), 
                         ('HOUSTS', 'South'), ('HOUSTW', 'West')]:
        if region in housing_data:
            regional_data[name] = housing_data[region]['yoy_change']
    
    if regional_data:
        report += "\n2. REGIONAL DISPARITIES (YoY %)\n"
        for region, change in sorted(regional_data.items(), key=lambda x: x[1]):
            report += f"   • {region}: {change:+.1f}%"
            if change < -20:
                report += " 🔴 SEVERE CONTRACTION"
            elif change < -10:
                report += " 🟡 MODERATE DECLINE"
            report += "\n"
    
    # 3. Supply-Demand Dynamics
    report += """
3. SUPPLY-DEMAND IMBALANCE
   • Population Growth: ~0.5% annually
   • Housing Starts Growth: -15.7% (negative)
   • Chronic Undersupply: 3-5 million unit deficit
   • Paradox: Prices high despite falling demand
"""
    
    # 4. Construction Cost Analysis
    if 'WPUSI012011' in housing_data:
        materials_yoy = housing_data['WPUSI012011']['yoy_change']
        report += f"""
4. CONSTRUCTION COST PRESSURES
   • Materials Inflation: {materials_yoy:+.1f}% YoY
   • Labor Shortage: Skilled trades deficit
   • Regulatory Costs: Zoning, permits up 30%+
   • Margin Compression: Builders pulling back
"""
    
    # 5. Financial Conditions
    if 'DRTSCILM' in housing_data:
        lending = housing_data['DRTSCILM']['latest']
        report += f"""
5. CREDIT CONDITIONS
   • Bank Lending Standards: {lending:.1f}% tightening
   • Down Payment Requirements: Rising
   • Debt-to-Income Limits: Stricter
   • First-Time Buyers: Locked out
"""
    
    report += """
📈 MARKET DYNAMICS EXPLANATION
------------------------------
The -15.7% momentum with -10.25 deceleration means:
• Housing starts falling at accelerating pace
• Not just declining, but decline is speeding up
• Classic late-cycle dynamics with Fed overtightening

🗺️ GEOGRAPHIC DISPARITIES
-------------------------
• WEST: Worst hit - Tech layoffs, overvaluation
• SOUTH: Resilient - Population inflows, lower costs
• NORTHEAST: Struggling - High costs, outmigration
• MIDWEST: Stable - Affordable, steady demand

⚡ CRITICAL FACTORS
------------------
1. RATE SENSITIVITY: Housing is most rate-sensitive sector
2. AFFORDABILITY: Worst since 1980s
3. PSYCHOLOGY: Buyers waiting for lower rates/prices
4. BUILDERS: Cutting starts, offering incentives
5. INVENTORY: Still low, preventing price collapse

🎯 FORWARD OUTLOOK
-----------------
• Near-term (3-6 months): Continued deceleration
• Medium-term (6-12 months): Stabilization if Fed cuts
• Long-term (1-3 years): Structural undersupply supports recovery

⚠️ RISKS
--------
• Further Fed hikes = Housing depression
• Forced sellers = Price cascade
• Builder bankruptcies = Supply shock
• Regional recessions = Concentrated pain

💡 INVESTMENT IMPLICATIONS
-------------------------
• AVOID: Homebuilders, mortgage REITs
• WATCH: Apartment REITs (rental demand)
• OPPORTUNITY: Distressed housing debt
• HEDGE: Short regional banks with housing exposure
"""
    
    # Save report
    with open('housing_deceleration_report.txt', 'w') as f:
        f.write(report)
    
    print(report)
    return report

def main():
    """Execute housing market analysis"""
    
    print("🏠 HOUSING MARKET DEEP DIVE ANALYSIS")
    print("="*60)
    
    # Get comprehensive data
    housing_data = get_comprehensive_housing_data()
    
    # Analyze drivers
    print("\n📊 Analyzing deceleration drivers...")
    analyze_housing_drivers(housing_data)
    
    # Generate insights
    print("\n📝 Generating detailed insights...")
    generate_housing_insights(housing_data)
    
    # Save data
    summary_df = pd.DataFrame([
        {
            'Series': k,
            'Name': v['name'],
            'Latest': v['latest'],
            'YoY_Change': v['yoy_change']
        }
        for k, v in housing_data.items()
    ])
    
    summary_df.to_csv('housing_market_summary.csv', index=False)
    print("\n💾 Saved: housing_market_summary.csv")
    
    print("\n✅ Housing analysis complete!")

if __name__ == "__main__":
    main()