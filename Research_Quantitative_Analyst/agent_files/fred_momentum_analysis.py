#!/usr/bin/env python3
"""
FRED Momentum Analysis - Acceleration/Deceleration Detection
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Identify accelerating/decelerating trends and reversals with interpretation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def calculate_momentum_metrics(data, series_name):
    """Calculate comprehensive momentum metrics"""
    
    # Basic momentum
    mom_1m = data.pct_change(periods=1) * 100
    mom_3m = data.pct_change(periods=3) * 100
    mom_6m = data.pct_change(periods=6) * 100
    mom_12m = data.pct_change(periods=12) * 100
    
    # Moving averages
    ma_20 = data.rolling(window=20).mean()
    ma_50 = data.rolling(window=50).mean()
    ma_200 = data.rolling(window=200).mean()
    
    # Rate of change of momentum (acceleration)
    mom_acceleration = mom_3m.diff()
    
    # Trend strength (regression slope)
    def calculate_trend_strength(series, window=60):
        """Calculate rolling regression slope"""
        slopes = []
        for i in range(window, len(series)):
            y = series.iloc[i-window:i].values
            x = np.arange(window)
            if not np.isnan(y).any():
                slope, _, _, _, _ = stats.linregress(x, y)
                slopes.append(slope)
            else:
                slopes.append(np.nan)
        return pd.Series(slopes, index=series.index[window:])
    
    trend_strength = calculate_trend_strength(data)
    
    # Regime detection
    bull_market = (ma_50 > ma_200) & (data > ma_50)
    bear_market = (ma_50 < ma_200) & (data < ma_50)
    
    # Recent metrics (last 6 months)
    recent_data = data.last('6M')
    if len(recent_data) > 0:
        recent_trend = stats.linregress(np.arange(len(recent_data)), recent_data.values)
        recent_acceleration = mom_acceleration.last('3M').mean()
    else:
        recent_trend = None
        recent_acceleration = np.nan
    
    return {
        'series_name': series_name,
        'current_value': data.iloc[-1] if len(data) > 0 else np.nan,
        'mom_1m': mom_1m.iloc[-1] if len(mom_1m) > 0 else np.nan,
        'mom_3m': mom_3m.iloc[-1] if len(mom_3m) > 0 else np.nan,
        'mom_6m': mom_6m.iloc[-1] if len(mom_6m) > 0 else np.nan,
        'mom_12m': mom_12m.iloc[-1] if len(mom_12m) > 0 else np.nan,
        'acceleration_3m': recent_acceleration,
        'trend_slope_6m': recent_trend.slope if recent_trend else np.nan,
        'above_ma50': (data.iloc[-1] > ma_50.iloc[-1]) if len(data) > 0 and len(ma_50) > 0 else np.nan,
        'above_ma200': (data.iloc[-1] > ma_200.iloc[-1]) if len(data) > 0 and len(ma_200) > 0 else np.nan,
        'regime': 'Bull' if bull_market.iloc[-1] else ('Bear' if bear_market.iloc[-1] else 'Neutral') if len(bull_market) > 0 else 'Unknown',
        'momentum_series': mom_3m,
        'acceleration_series': mom_acceleration,
        'data': data
    }

def analyze_all_series():
    """Analyze momentum for all series"""
    
    print("📊 Loading historical data...")
    # Load the historical data we saved
    df = pd.read_csv('fred_historical_data_10y.csv', index_col=0, parse_dates=True)
    
    print(f"✅ Loaded {len(df.columns)} series with {len(df)} observations")
    
    # Analyze each series
    momentum_results = []
    
    for column in df.columns:
        series_data = df[column].dropna()
        if len(series_data) > 20:  # Need minimum data
            metrics = calculate_momentum_metrics(series_data, column)
            momentum_results.append(metrics)
    
    # Convert to DataFrame for analysis
    momentum_df = pd.DataFrame(momentum_results)
    
    # Sort by different criteria
    accelerating = momentum_df[momentum_df['acceleration_3m'] > 0.5].sort_values('acceleration_3m', ascending=False)
    decelerating = momentum_df[momentum_df['acceleration_3m'] < -0.5].sort_values('acceleration_3m')
    trend_reversing = momentum_df[
        ((momentum_df['mom_3m'] > 0) & (momentum_df['mom_12m'] < 0)) |
        ((momentum_df['mom_3m'] < 0) & (momentum_df['mom_12m'] > 0))
    ]
    
    return momentum_df, accelerating, decelerating, trend_reversing

def create_momentum_dashboard(momentum_df, accelerating, decelerating, trend_reversing):
    """Create comprehensive momentum visualization"""
    
    fig = plt.figure(figsize=(20, 24))
    
    # 1. Top Accelerating Series
    ax1 = plt.subplot(4, 2, 1)
    if len(accelerating) > 0:
        top_accel = accelerating.head(10)
        ax1.barh(top_accel['series_name'], top_accel['acceleration_3m'], color='green')
        ax1.set_title('Top 10 Accelerating Series (3M Momentum Change)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Acceleration Rate')
        
        # Add current momentum values
        for i, (idx, row) in enumerate(top_accel.iterrows()):
            ax1.text(row['acceleration_3m'] + 0.1, i, f"{row['mom_3m']:.1f}%", 
                    va='center', fontsize=9)
    
    # 2. Top Decelerating Series
    ax2 = plt.subplot(4, 2, 2)
    if len(decelerating) > 0:
        top_decel = decelerating.head(10)
        ax2.barh(top_decel['series_name'], top_decel['acceleration_3m'], color='red')
        ax2.set_title('Top 10 Decelerating Series (3M Momentum Change)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Deceleration Rate')
        
        # Add current momentum values
        for i, (idx, row) in enumerate(top_decel.iterrows()):
            ax2.text(row['acceleration_3m'] - 0.1, i, f"{row['mom_3m']:.1f}%", 
                    va='center', ha='right', fontsize=9)
    
    # 3. Momentum Heatmap
    ax3 = plt.subplot(4, 2, 3)
    # Create momentum matrix
    mom_matrix = momentum_df[['series_name', 'mom_1m', 'mom_3m', 'mom_6m', 'mom_12m']].set_index('series_name')
    mom_matrix = mom_matrix.sort_values('mom_3m', ascending=False).head(20)
    
    sns.heatmap(mom_matrix, annot=True, fmt='.1f', cmap='RdYlGn', center=0, 
                ax=ax3, cbar_kws={'label': 'Momentum %'})
    ax3.set_title('Momentum Heatmap (Top 20 by 3M Momentum)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Time Period')
    
    # 4. Trend Reversals
    ax4 = plt.subplot(4, 2, 4)
    if len(trend_reversing) > 0:
        reversal_data = trend_reversing[['series_name', 'mom_3m', 'mom_12m']].head(10)
        x = np.arange(len(reversal_data))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, reversal_data['mom_3m'], width, label='3M Momentum', color='blue')
        bars2 = ax4.bar(x + width/2, reversal_data['mom_12m'], width, label='12M Momentum', color='orange')
        
        ax4.set_xlabel('Series')
        ax4.set_ylabel('Momentum %')
        ax4.set_title('Trend Reversing Series (3M vs 12M)', fontsize=14, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(reversal_data['series_name'], rotation=45, ha='right')
        ax4.legend()
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # 5. Regime Distribution
    ax5 = plt.subplot(4, 2, 5)
    regime_counts = momentum_df['regime'].value_counts()
    colors = {'Bull': 'green', 'Bear': 'red', 'Neutral': 'gray', 'Unknown': 'lightgray'}
    ax5.pie(regime_counts.values, labels=regime_counts.index, autopct='%1.1f%%',
            colors=[colors.get(x, 'gray') for x in regime_counts.index])
    ax5.set_title('Market Regime Distribution', fontsize=14, fontweight='bold')
    
    # 6. Momentum vs Acceleration Scatter
    ax6 = plt.subplot(4, 2, 6)
    # Color by regime
    regime_colors = {'Bull': 'green', 'Bear': 'red', 'Neutral': 'gray', 'Unknown': 'lightgray'}
    colors = [regime_colors.get(r, 'gray') for r in momentum_df['regime']]
    
    scatter = ax6.scatter(momentum_df['mom_3m'], momentum_df['acceleration_3m'], 
                         c=colors, alpha=0.6, s=100)
    
    # Add quadrant lines
    ax6.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax6.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    
    # Label quadrants
    ax6.text(15, 3, 'Accelerating\nGrowth', ha='center', va='center', fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.5))
    ax6.text(-15, 3, 'Decelerating\nDecline', ha='center', va='center', fontsize=12,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5))
    ax6.text(15, -3, 'Decelerating\nGrowth', ha='center', va='center', fontsize=12,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="orange", alpha=0.5))
    ax6.text(-15, -3, 'Accelerating\nDecline', ha='center', va='center', fontsize=12,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.5))
    
    ax6.set_xlabel('3-Month Momentum %')
    ax6.set_ylabel('3-Month Acceleration')
    ax6.set_title('Momentum vs Acceleration Analysis', fontsize=14, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # 7. Key Series Deep Dive
    ax7 = plt.subplot(4, 1, 4)
    key_series = ['GDPC1', 'UNRATE', 'CPIAUCSL', 'SP500', 'DGS10', 'VIXCLS']
    available_key = [s for s in key_series if s in momentum_df['series_name'].values]
    
    if available_key:
        for series in available_key:
            series_data = momentum_df[momentum_df['series_name'] == series].iloc[0]
            mom_series = series_data['momentum_series'].last('2Y')
            ax7.plot(mom_series.index, mom_series.values, linewidth=2, label=series)
        
        ax7.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax7.set_title('Key Economic Indicators - 3M Momentum (Last 2 Years)', fontsize=14, fontweight='bold')
        ax7.set_ylabel('3-Month Momentum %')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
    
    plt.suptitle('MOMENTUM ANALYSIS DASHBOARD - Acceleration & Trend Reversals', 
                fontsize=18, fontweight='bold')
    plt.tight_layout()
    plt.savefig('fred_momentum_analysis.png', dpi=300, bbox_inches='tight')
    print("💾 Saved: fred_momentum_analysis.png")

def generate_interpretation_report(momentum_df, accelerating, decelerating, trend_reversing):
    """Generate detailed interpretation of momentum findings"""
    
    report = """
📊 MOMENTUM ANALYSIS INTERPRETATION REPORT
==========================================

🚀 ACCELERATING MOMENTUM (Positive Acceleration)
"""
    
    if len(accelerating) > 0:
        report += "\nTop 5 Accelerating Series:\n"
        for idx, row in accelerating.head(5).iterrows():
            report += f"• {row['series_name']}: {row['mom_3m']:.1f}% momentum, +{row['acceleration_3m']:.2f} acceleration\n"
            
            # Interpretation
            if row['series_name'] == 'UNRATE':
                report += "  → Unemployment accelerating = Labor market weakening rapidly\n"
            elif row['series_name'] in ['CPIAUCSL', 'CPILFESL', 'PCEPI']:
                report += "  → Inflation reaccelerating = Fed may need to act\n"
            elif row['series_name'] == 'VIXCLS':
                report += "  → Volatility surging = Risk-off environment developing\n"
            elif row['series_name'] in ['SP500', 'DJIA']:
                report += "  → Equity momentum building = Bull market strengthening\n"
            elif row['series_name'] == 'DGS10':
                report += "  → Bond yields rising fast = Rate expectations shifting\n"
    
    report += """
📉 DECELERATING MOMENTUM (Negative Acceleration)
"""
    
    if len(decelerating) > 0:
        report += "\nTop 5 Decelerating Series:\n"
        for idx, row in decelerating.head(5).iterrows():
            report += f"• {row['series_name']}: {row['mom_3m']:.1f}% momentum, {row['acceleration_3m']:.2f} deceleration\n"
            
            # Interpretation
            if row['series_name'] == 'GDPC1':
                report += "  → GDP growth slowing = Economic momentum fading\n"
            elif row['series_name'] in ['M2SL', 'TOTBKCR']:
                report += "  → Money supply/credit contracting = Tightening conditions\n"
            elif row['series_name'] == 'HOUST':
                report += "  → Housing starts slowing = Real estate cooling\n"
            elif row['series_name'] == 'INDPRO':
                report += "  → Industrial production weakening = Manufacturing slowdown\n"
    
    report += """
🔄 TREND REVERSALS (Diverging 3M vs 12M)
"""
    
    if len(trend_reversing) > 0:
        report += "\nNotable Trend Reversals:\n"
        for idx, row in trend_reversing.head(5).iterrows():
            report += f"• {row['series_name']}: 3M={row['mom_3m']:.1f}%, 12M={row['mom_12m']:.1f}%\n"
            
            if row['mom_3m'] > 0 and row['mom_12m'] < 0:
                report += "  → Bottoming out - Early recovery signal\n"
            else:
                report += "  → Topping out - Early weakness signal\n"
    
    # Market regime analysis
    regime_counts = momentum_df['regime'].value_counts()
    total = len(momentum_df)
    
    report += f"""
📈 MARKET REGIME ANALYSIS
========================
• Bull Market: {regime_counts.get('Bull', 0)} series ({regime_counts.get('Bull', 0)/total*100:.1f}%)
• Bear Market: {regime_counts.get('Bear', 0)} series ({regime_counts.get('Bear', 0)/total*100:.1f}%)
• Neutral: {regime_counts.get('Neutral', 0)} series ({regime_counts.get('Neutral', 0)/total*100:.1f}%)

🎯 KEY INSIGHTS FOR TRADING/POLICY
==================================
"""
    
    # Generate actionable insights
    # Check inflation momentum
    inflation_accel = momentum_df[momentum_df['series_name'].isin(['CPIAUCSL', 'CPILFESL', 'PCEPI'])]['acceleration_3m'].mean()
    if inflation_accel > 0:
        report += "1. INFLATION: Reaccelerating - Bearish for bonds, hawkish Fed risk\n"
    else:
        report += "1. INFLATION: Decelerating - Bullish for bonds, dovish Fed possible\n"
    
    # Check growth momentum  
    growth_indicators = ['GDPC1', 'INDPRO', 'PAYEMS']
    growth_accel = momentum_df[momentum_df['series_name'].isin(growth_indicators)]['acceleration_3m'].mean()
    if growth_accel > 0:
        report += "2. GROWTH: Accelerating - Risk-on, cyclicals outperform\n"
    else:
        report += "2. GROWTH: Decelerating - Risk-off, defensives outperform\n"
    
    # Check financial conditions
    if 'VIXCLS' in momentum_df['series_name'].values:
        vix_mom = momentum_df[momentum_df['series_name'] == 'VIXCLS']['mom_3m'].values[0]
        if vix_mom > 20:
            report += "3. RISK: VIX surging - Hedge portfolios, reduce leverage\n"
        elif vix_mom < -20:
            report += "3. RISK: VIX collapsing - Add risk, sell volatility\n"
    
    # Yield curve
    if 'T10Y2Y' in momentum_df['series_name'].values:
        curve_accel = momentum_df[momentum_df['series_name'] == 'T10Y2Y']['acceleration_3m'].values[0]
        if curve_accel > 0:
            report += "4. YIELD CURVE: Steepening - Banks outperform, growth expectations rising\n"
        else:
            report += "4. YIELD CURVE: Flattening - Recession risk, defensive positioning\n"
    
    report += """
⚡ MOMENTUM TRADING SIGNALS
==========================
Strong Buy: Series with positive momentum AND positive acceleration
Strong Sell: Series with negative momentum AND negative acceleration  
Reversal Watch: Series where 3M and 12M momentum diverge significantly
Mean Reversion: Series with extreme momentum readings (>±20%)

📊 STATISTICAL SIGNIFICANCE
==========================
• Acceleration > 1.0 or < -1.0: Highly significant momentum shift
• Momentum > 10% or < -10%: Strong directional move
• Regime changes: Monitor series crossing MA50/MA200
"""
    
    # Save report
    with open('fred_momentum_interpretation.txt', 'w') as f:
        f.write(report)
    
    print(report)
    return report

def main():
    """Execute momentum analysis"""
    
    print("🎯 MOMENTUM ACCELERATION/DECELERATION ANALYSIS")
    print("="*60)
    
    # Analyze all series
    momentum_df, accelerating, decelerating, trend_reversing = analyze_all_series()
    
    print(f"\n📊 Analysis Results:")
    print(f"   Accelerating series: {len(accelerating)}")
    print(f"   Decelerating series: {len(decelerating)}")
    print(f"   Trend reversing: {len(trend_reversing)}")
    
    # Create visualizations
    print("\n🎨 Creating momentum dashboard...")
    create_momentum_dashboard(momentum_df, accelerating, decelerating, trend_reversing)
    
    # Generate interpretation
    print("\n📝 Generating interpretation report...")
    generate_interpretation_report(momentum_df, accelerating, decelerating, trend_reversing)
    
    # Save detailed results
    momentum_df.to_csv('fred_momentum_metrics.csv', index=False)
    print("\n💾 Saved detailed metrics to: fred_momentum_metrics.csv")
    
    print("\n✅ Momentum analysis complete!")

if __name__ == "__main__":
    main()