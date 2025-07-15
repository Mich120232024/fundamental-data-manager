#!/usr/bin/env python3
"""
FRED Comprehensive Macroeconomic Analysis
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Analyze all collected FRED data to understand current economic picture
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_all_data():
    """Load all FRED data files"""
    print("📊 Loading FRED data files...")
    
    # Load the main datasets
    df_200 = pd.read_csv('fred_200_series_data.csv')
    df_24 = pd.read_csv('fred_key_indicators_latest.csv')
    
    # Convert date columns
    df_200['latest_date'] = pd.to_datetime(df_200['latest_date'])
    df_24['latest_date'] = pd.to_datetime(df_24['latest_date'])
    
    # Combine datasets (removing duplicates)
    all_series = pd.concat([df_200, df_24], ignore_index=True)
    all_series = all_series.drop_duplicates(subset=['series_id'], keep='first')
    
    print(f"✅ Loaded {len(all_series)} unique series")
    return all_series

def create_economic_dashboard(df):
    """Create comprehensive economic dashboard"""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 24))
    
    # Define grid
    gs = fig.add_gridspec(6, 3, hspace=0.3, wspace=0.3)
    
    # 1. Key Economic Indicators Summary
    ax1 = fig.add_subplot(gs[0, :])
    key_indicators = {
        'GDP Growth': df[df['series_id'] == 'GDPC1']['latest_value'].values[0] if 'GDPC1' in df['series_id'].values else 'N/A',
        'Unemployment': df[df['series_id'] == 'UNRATE']['latest_value'].values[0] if 'UNRATE' in df['series_id'].values else 'N/A',
        'CPI Inflation': df[df['series_id'] == 'CPIAUCSL']['latest_value'].values[0] if 'CPIAUCSL' in df['series_id'].values else 'N/A',
        'Fed Funds': df[df['series_id'] == 'FEDFUNDS']['latest_value'].values[0] if 'FEDFUNDS' in df['series_id'].values else 'N/A',
        'S&P 500': df[df['series_id'] == 'SP500']['latest_value'].values[0] if 'SP500' in df['series_id'].values else 'N/A',
        '10Y Treasury': df[df['series_id'] == 'DGS10']['latest_value'].values[0] if 'DGS10' in df['series_id'].values else 'N/A'
    }
    
    ax1.axis('off')
    text = "🏛️ KEY ECONOMIC INDICATORS (Latest Values)\n\n"
    for indicator, value in key_indicators.items():
        if value != 'N/A':
            if indicator in ['GDP Growth']:
                text += f"{indicator}: ${value:,.0f}B | "
            elif indicator in ['Unemployment', 'CPI Inflation', 'Fed Funds', '10Y Treasury']:
                text += f"{indicator}: {value:.2f}% | "
            else:
                text += f"{indicator}: {value:,.0f} | "
    ax1.text(0.5, 0.5, text.rstrip(' | '), ha='center', va='center', fontsize=14, 
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.5))
    
    # 2. Category Distribution
    ax2 = fig.add_subplot(gs[1, 0])
    if 'category' in df.columns:
        category_counts = df['category'].value_counts()
        ax2.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
        ax2.set_title('Series Distribution by Category', fontsize=12, fontweight='bold')
    
    # 3. Update Frequency Analysis
    ax3 = fig.add_subplot(gs[1, 1])
    freq_counts = df['frequency'].value_counts()
    ax3.bar(freq_counts.index, freq_counts.values)
    ax3.set_title('Data Update Frequency', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Frequency')
    ax3.set_ylabel('Number of Series')
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # 4. Recent Updates Timeline
    ax4 = fig.add_subplot(gs[1, 2])
    df['days_since_update'] = (datetime.now() - df['latest_date']).dt.days
    recent_updates = df.nsmallest(20, 'days_since_update')[['series_id', 'days_since_update']]
    ax4.barh(recent_updates['series_id'], recent_updates['days_since_update'])
    ax4.set_title('Most Recently Updated Series', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Days Since Update')
    
    # 5. Interest Rate Analysis
    ax5 = fig.add_subplot(gs[2, :])
    rate_series = ['DGS1', 'DGS2', 'DGS5', 'DGS10', 'DGS30']
    rate_data = []
    for series in rate_series:
        if series in df['series_id'].values:
            value = df[df['series_id'] == series]['latest_value'].values[0]
            maturity = series.replace('DGS', '')
            rate_data.append({'Maturity': maturity, 'Rate': value})
    
    if rate_data:
        rate_df = pd.DataFrame(rate_data)
        rate_df['Maturity_Num'] = rate_df['Maturity'].astype(float)
        rate_df = rate_df.sort_values('Maturity_Num')
        ax5.plot(rate_df['Maturity'], rate_df['Rate'], marker='o', linewidth=2, markersize=8)
        ax5.set_title('US Treasury Yield Curve', fontsize=14, fontweight='bold')
        ax5.set_xlabel('Maturity (Years)')
        ax5.set_ylabel('Yield (%)')
        ax5.grid(True, alpha=0.3)
    
    # 6. Economic Health Indicators
    ax6 = fig.add_subplot(gs[3, 0])
    health_indicators = {
        'Unemployment Rate': ('UNRATE', 4.2, 'lower'),  # target, direction
        'Core PCE Inflation': ('PCEPILFE', 2.0, 'target'),
        'Industrial Production': ('INDPRO', 100, 'higher'),
        'Consumer Sentiment': ('UMCSENT', 80, 'higher'),
        'Capacity Utilization': ('MCUMFN', 80, 'target')
    }
    
    health_data = []
    for name, (series_id, target, direction) in health_indicators.items():
        if series_id in df['series_id'].values:
            value = df[df['series_id'] == series_id]['latest_value'].values[0]
            if direction == 'lower':
                score = max(0, min(100, 100 * (target / value)))
            elif direction == 'higher':
                score = max(0, min(100, 100 * (value / target)))
            else:  # target
                score = max(0, 100 - abs(value - target) * 10)
            health_data.append({'Indicator': name, 'Score': score, 'Value': value})
    
    if health_data:
        health_df = pd.DataFrame(health_data)
        colors = ['green' if s >= 80 else 'yellow' if s >= 60 else 'red' for s in health_df['Score']]
        ax6.barh(health_df['Indicator'], health_df['Score'], color=colors)
        ax6.set_xlim(0, 100)
        ax6.set_title('Economic Health Scorecard', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Health Score (0-100)')
    
    # 7. Market Performance
    ax7 = fig.add_subplot(gs[3, 1])
    market_series = {
        'S&P 500': 'SP500',
        'Dow Jones': 'DJIA',
        'NASDAQ': 'NASDAQCOM',
        'VIX': 'VIXCLS',
        'Oil (WTI)': 'DCOILWTICO',
        'Gold': 'GOLDAMGBD228NLBM'
    }
    
    market_data = []
    for name, series_id in market_series.items():
        if series_id in df['series_id'].values:
            value = df[df['series_id'] == series_id]['latest_value'].values[0]
            market_data.append({'Asset': name, 'Value': value})
    
    if market_data:
        market_df = pd.DataFrame(market_data)
        # Normalize values for visualization
        market_df['Normalized'] = market_df['Value'] / market_df['Value'].max() * 100
        ax7.bar(market_df['Asset'], market_df['Normalized'])
        ax7.set_title('Market Performance (Normalized)', fontsize=12, fontweight='bold')
        ax7.set_ylabel('Relative Value')
        plt.setp(ax7.xaxis.get_majorticklabels(), rotation=45)
    
    # 8. Money Supply & Credit
    ax8 = fig.add_subplot(gs[3, 2])
    money_series = {
        'M2 Money Supply': 'M2SL',
        'Bank Credit': 'TOTBKCR',
        'Business Loans': 'BUSLOANS',
        'Consumer Credit': 'TOTALSL',
        'Fed Balance Sheet': 'BOGMBASE'
    }
    
    money_data = []
    for name, series_id in money_series.items():
        if series_id in df['series_id'].values:
            value = df[df['series_id'] == series_id]['latest_value'].values[0]
            money_data.append({'Measure': name, 'Value': value})
    
    if money_data:
        money_df = pd.DataFrame(money_data)
        ax8.barh(money_df['Measure'], money_df['Value'])
        ax8.set_title('Money Supply & Credit Metrics', fontsize=12, fontweight='bold')
        ax8.set_xlabel('Billions USD')
    
    # 9. Data Quality Metrics
    ax9 = fig.add_subplot(gs[4, :])
    ax9.axis('off')
    
    # Calculate data quality metrics
    total_series = len(df)
    daily_series = len(df[df['frequency'] == 'Daily'])
    recent_updates = len(df[df['days_since_update'] <= 7])
    avg_days_since = df['days_since_update'].mean()
    
    quality_text = f"""📊 DATA QUALITY METRICS
    
Total Economic Series: {total_series}
Daily Updated Series: {daily_series} ({daily_series/total_series*100:.1f}%)
Updated Within 7 Days: {recent_updates} ({recent_updates/total_series*100:.1f}%)
Average Days Since Update: {avg_days_since:.1f}
Data Coverage Period: {df['latest_date'].min().strftime('%Y-%m-%d')} to {df['latest_date'].max().strftime('%Y-%m-%d')}
"""
    
    ax9.text(0.5, 0.5, quality_text, ha='center', va='center', fontsize=12,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.5))
    
    # 10. Economic Summary Analysis
    ax10 = fig.add_subplot(gs[5, :])
    ax10.axis('off')
    
    # Generate economic summary
    summary = generate_economic_summary(df)
    ax10.text(0.5, 0.5, summary, ha='center', va='center', fontsize=11,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.3),
             wrap=True)
    
    plt.suptitle('FRED COMPREHENSIVE MACROECONOMIC DASHBOARD', fontsize=20, fontweight='bold')
    plt.tight_layout()
    
    # Save the dashboard
    plt.savefig('fred_economic_dashboard.png', dpi=300, bbox_inches='tight')
    print("💾 Dashboard saved to: fred_economic_dashboard.png")
    
    return fig

def generate_economic_summary(df):
    """Generate narrative economic summary"""
    
    # Extract key values
    gdp = df[df['series_id'] == 'GDPC1']['latest_value'].values[0] if 'GDPC1' in df['series_id'].values else None
    unemployment = df[df['series_id'] == 'UNRATE']['latest_value'].values[0] if 'UNRATE' in df['series_id'].values else None
    cpi = df[df['series_id'] == 'CPIAUCSL']['latest_value'].values[0] if 'CPIAUCSL' in df['series_id'].values else None
    fed_funds = df[df['series_id'] == 'FEDFUNDS']['latest_value'].values[0] if 'FEDFUNDS' in df['series_id'].values else None
    ten_year = df[df['series_id'] == 'DGS10']['latest_value'].values[0] if 'DGS10' in df['series_id'].values else None
    sp500 = df[df['series_id'] == 'SP500']['latest_value'].values[0] if 'SP500' in df['series_id'].values else None
    vix = df[df['series_id'] == 'VIXCLS']['latest_value'].values[0] if 'VIXCLS' in df['series_id'].values else None
    
    summary = "📈 ECONOMIC SUMMARY (June 2025)\n\n"
    
    # Growth assessment
    if gdp:
        summary += f"GROWTH: Real GDP at ${gdp:,.0f}B indicates "
        summary += "solid economic expansion. "
    
    # Labor market
    if unemployment:
        summary += f"LABOR: Unemployment at {unemployment:.1f}% suggests "
        if unemployment < 4.0:
            summary += "tight labor market conditions. "
        elif unemployment > 5.0:
            summary += "weakening labor market. "
        else:
            summary += "balanced employment levels. "
    
    # Monetary policy
    if fed_funds and ten_year:
        spread = ten_year - fed_funds
        summary += f"RATES: Fed Funds at {fed_funds:.2f}% with 10Y at {ten_year:.2f}% "
        if spread < 0:
            summary += "shows inverted yield curve - recession signal. "
        else:
            summary += f"gives {spread:.2f}% term spread. "
    
    # Markets
    if sp500 and vix:
        summary += f"MARKETS: S&P at {sp500:,.0f} with VIX at {vix:.1f} indicates "
        if vix < 20:
            summary += "low volatility/complacent markets. "
        else:
            summary += "elevated market uncertainty. "
    
    # Overall assessment
    summary += "\n\nOVERALL: The data suggests "
    if unemployment and unemployment < 4.5 and vix and vix < 20:
        summary += "a stable economic environment with tight labor markets and calm financial conditions."
    else:
        summary += "mixed economic signals requiring careful monitoring of inflation and growth dynamics."
    
    return summary

def create_correlation_analysis(df):
    """Create correlation matrix of key indicators"""
    
    # Select key series for correlation
    key_series = ['UNRATE', 'CPIAUCSL', 'FEDFUNDS', 'DGS10', 'SP500', 'VIXCLS',
                  'INDPRO', 'PAYEMS', 'HOUST', 'DCOILWTICO', 'M2SL', 'UMCSENT']
    
    # Filter available series
    available = [s for s in key_series if s in df['series_id'].values]
    
    if len(available) > 3:
        # Create pivot table
        corr_data = df[df['series_id'].isin(available)][['series_id', 'latest_value']]
        corr_pivot = corr_data.set_index('series_id').T
        
        # Calculate correlation
        correlation = corr_pivot.corr()
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0,
                    square=True, linewidths=1, cbar_kws={"shrink": .8})
        plt.title('Economic Indicators Correlation Matrix', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('fred_correlation_matrix.png', dpi=300)
        print("💾 Correlation matrix saved to: fred_correlation_matrix.png")

def main():
    """Run comprehensive analysis"""
    
    print("🚀 Starting FRED Comprehensive Economic Analysis")
    print("="*60)
    
    # Load data
    df = load_all_data()
    
    # Create visualizations
    print("\n📊 Creating economic dashboard...")
    create_economic_dashboard(df)
    
    print("\n🔗 Analyzing correlations...")
    create_correlation_analysis(df)
    
    # Generate statistical summary
    print("\n📈 Statistical Summary:")
    print(f"Total Series: {len(df)}")
    print(f"Categories: {df['category'].nunique() if 'category' in df.columns else 'N/A'}")
    print(f"Date Range: {df['latest_date'].min()} to {df['latest_date'].max()}")
    print(f"Most Common Frequency: {df['frequency'].mode()[0]}")
    
    # Save comprehensive dataset
    df.to_csv('fred_comprehensive_dataset.csv', index=False)
    print("\n💾 Comprehensive dataset saved to: fred_comprehensive_dataset.csv")
    
    print("\n✅ Analysis complete! Check generated files:")
    print("   - fred_economic_dashboard.png")
    print("   - fred_correlation_matrix.png")
    print("   - fred_comprehensive_dataset.csv")

if __name__ == "__main__":
    main()