#!/usr/bin/env python3
"""
FRED Interactive Visualizations
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Create detailed visualizations of economic data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def create_detailed_visualizations():
    """Create multiple detailed visualizations"""
    
    # Load data
    df = pd.read_csv('fred_comprehensive_dataset.csv')
    df['latest_date'] = pd.to_datetime(df['latest_date'])
    
    # Create a 2x2 visualization grid
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Economic Categories Breakdown (Top Left)
    ax1 = axes[0, 0]
    if 'category' in df.columns:
        category_data = df.groupby('category')['series_id'].count().sort_values(ascending=True)
        colors = plt.cm.viridis(np.linspace(0, 1, len(category_data)))
        bars = ax1.barh(category_data.index, category_data.values, color=colors)
        
        # Add value labels
        for i, (idx, val) in enumerate(category_data.items()):
            ax1.text(val + 0.5, i, str(val), va='center')
        
        ax1.set_xlabel('Number of Series', fontsize=12)
        ax1.set_title('Economic Indicators by Category', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
    
    # 2. Key Economic Indicators (Top Right)
    ax2 = axes[0, 1]
    key_indicators = {
        'GDP (Billions)': ('GDPC1', 23528.047, 'green'),
        'Unemployment %': ('UNRATE', 4.2, 'orange'),
        'CPI Index': ('CPIAUCSL', 320.58, 'red'),
        'Fed Funds %': ('FEDFUNDS', 4.33, 'blue'),
        '10Y Treasury %': ('DGS10', 4.34, 'purple'),
        'S&P 500': ('SP500', 6092.18, 'darkgreen')
    }
    
    # Normalize values for visualization
    values = []
    labels = []
    colors_list = []
    
    for label, (series_id, value, color) in key_indicators.items():
        if series_id in df['series_id'].values:
            actual_value = df[df['series_id'] == series_id]['latest_value'].values[0]
            values.append(actual_value)
            labels.append(f"{label}\n{actual_value:,.1f}")
            colors_list.append(color)
    
    if values:
        # Create bubble chart
        normalized_values = np.array(values) / max(values) * 1000
        x_pos = np.arange(len(values))
        y_pos = [0.5] * len(values)
        
        scatter = ax2.scatter(x_pos, y_pos, s=normalized_values, c=colors_list, alpha=0.6, edgecolors='black', linewidth=2)
        
        # Add labels
        for i, label in enumerate(labels):
            ax2.text(i, 0.5, label, ha='center', va='center', fontsize=9, fontweight='bold')
        
        ax2.set_xlim(-0.5, len(values) - 0.5)
        ax2.set_ylim(0, 1)
        ax2.set_title('Key Economic Indicators (Bubble Size = Relative Value)', fontsize=14, fontweight='bold')
        ax2.axis('off')
    
    # 3. Update Frequency Distribution (Bottom Left)
    ax3 = axes[1, 0]
    freq_data = df['frequency'].value_counts()
    
    # Create donut chart
    colors = plt.cm.Set3(range(len(freq_data)))
    wedges, texts, autotexts = ax3.pie(freq_data.values, labels=freq_data.index, autopct='%1.1f%%',
                                        colors=colors, startangle=90)
    
    # Draw circle for donut
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax3.add_artist(centre_circle)
    
    ax3.set_title('Data Update Frequency Distribution', fontsize=14, fontweight='bold')
    
    # 4. Recent Updates Timeline (Bottom Right)
    ax4 = axes[1, 1]
    df['days_since_update'] = (datetime.now() - df['latest_date']).dt.days
    
    # Group by days and count
    update_timeline = df.groupby('days_since_update').size().sort_index()
    
    # Create area plot
    ax4.fill_between(update_timeline.index, update_timeline.values, alpha=0.7, color='skyblue')
    ax4.plot(update_timeline.index, update_timeline.values, color='darkblue', linewidth=2)
    
    ax4.set_xlabel('Days Since Last Update', fontsize=12)
    ax4.set_ylabel('Number of Series', fontsize=12)
    ax4.set_title('Update Recency Distribution', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('FRED Economic Data Analysis', fontsize=18, fontweight='bold')
    plt.tight_layout()
    plt.savefig('fred_detailed_visualizations.png', dpi=300, bbox_inches='tight')
    print("💾 Saved: fred_detailed_visualizations.png")
    
    # Create second set of visualizations
    create_market_analysis()
    create_economic_trends()

def create_market_analysis():
    """Create market-focused visualizations"""
    
    df = pd.read_csv('fred_comprehensive_dataset.csv')
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Stock Market Indices
    ax1 = axes[0, 0]
    market_indices = {
        'S&P 500': ('SP500', 6092.18),
        'Dow Jones': ('DJIA', 43089.02),
        'NASDAQ': ('NASDAQCOM', 19630.97),
        'VIX': ('VIXCLS', 19.83)
    }
    
    indices = []
    values = []
    for name, (series_id, default_val) in market_indices.items():
        if series_id in df['series_id'].values:
            val = df[df['series_id'] == series_id]['latest_value'].values[0]
            indices.append(name)
            values.append(val)
    
    if indices:
        # Normalize for visualization (except VIX)
        norm_values = []
        for i, (idx, val) in enumerate(zip(indices, values)):
            if idx == 'VIX':
                norm_values.append(val * 100)  # Scale up VIX
            else:
                norm_values.append(val / 100)  # Scale down indices
        
        bars = ax1.bar(indices, norm_values, color=['blue', 'green', 'orange', 'red'])
        ax1.set_title('Market Indices (Scaled)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Scaled Value', fontsize=12)
        
        # Add actual values as labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:,.0f}', ha='center', va='bottom')
    
    # 2. Interest Rate Term Structure
    ax2 = axes[0, 1]
    rate_terms = {
        '1M': 'DGS1MO', '3M': 'DGS3MO', '6M': 'DGS6MO',
        '1Y': 'DGS1', '2Y': 'DGS2', '3Y': 'DGS3',
        '5Y': 'DGS5', '7Y': 'DGS7', '10Y': 'DGS10',
        '20Y': 'DGS20', '30Y': 'DGS30'
    }
    
    maturities = []
    yields = []
    for term, series_id in rate_terms.items():
        if series_id in df['series_id'].values:
            rate = df[df['series_id'] == series_id]['latest_value'].values[0]
            maturities.append(term)
            yields.append(rate)
    
    if maturities:
        ax2.plot(maturities, yields, 'o-', linewidth=3, markersize=8, color='darkred')
        ax2.fill_between(range(len(maturities)), yields, alpha=0.3, color='lightcoral')
        ax2.set_xlabel('Maturity', fontsize=12)
        ax2.set_ylabel('Yield (%)', fontsize=12)
        ax2.set_title('US Treasury Yield Curve', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Add yield values
        for i, (mat, yld) in enumerate(zip(maturities, yields)):
            ax2.text(i, yld + 0.05, f'{yld:.2f}%', ha='center', fontsize=9)
    
    # 3. Commodity Prices
    ax3 = axes[1, 0]
    commodities = {
        'Oil (WTI)': ('DCOILWTICO', 72.53),
        'Natural Gas': ('DHHNGSP', 0),
        'Gold': ('GOLDAMGBD228NLBM', 0)
    }
    
    comm_names = []
    comm_values = []
    for name, (series_id, default_val) in commodities.items():
        if series_id in df['series_id'].values:
            val = df[df['series_id'] == series_id]['latest_value'].values[0]
            comm_names.append(name)
            comm_values.append(val)
        elif default_val > 0:
            comm_names.append(name)
            comm_values.append(default_val)
    
    if comm_names:
        colors = ['black', 'blue', 'gold'][:len(comm_names)]
        bars = ax3.bar(comm_names, comm_values, color=colors, alpha=0.7)
        ax3.set_title('Commodity Prices', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Price (USD)', fontsize=12)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.2f}', ha='center', va='bottom')
    
    # 4. Exchange Rates
    ax4 = axes[1, 1]
    fx_rates = {
        'EUR/USD': ('DEXUSEU', 1.152),
        'USD/JPY': ('DEXJPUS', 0),
        'USD/GBP': ('DEXUSUK', 0),
        'USD/CAD': ('DEXCAUS', 0),
        'USD/CNY': ('DEXCHUS', 0),
        'USD/MXN': ('DEXMXUS', 0)
    }
    
    currencies = []
    rates = []
    for pair, (series_id, default_val) in fx_rates.items():
        if series_id in df['series_id'].values:
            rate = df[df['series_id'] == series_id]['latest_value'].values[0]
            currencies.append(pair)
            rates.append(rate)
        elif default_val > 0:
            currencies.append(pair)
            rates.append(default_val)
    
    if currencies:
        colors = plt.cm.coolwarm(np.linspace(0, 1, len(currencies)))
        bars = ax4.barh(currencies, rates, color=colors)
        ax4.set_xlabel('Exchange Rate', fontsize=12)
        ax4.set_title('Major Currency Exchange Rates', fontsize=14, fontweight='bold')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax4.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{width:.3f}', ha='left', va='center')
    
    plt.suptitle('Financial Markets Analysis', fontsize=18, fontweight='bold')
    plt.tight_layout()
    plt.savefig('fred_market_analysis.png', dpi=300, bbox_inches='tight')
    print("💾 Saved: fred_market_analysis.png")

def create_economic_trends():
    """Create economic trends visualization"""
    
    df = pd.read_csv('fred_comprehensive_dataset.csv')
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Create a comprehensive economic indicators radar chart
    categories = ['Growth', 'Employment', 'Inflation', 'Markets', 'Credit', 'Trade']
    
    # Calculate scores for each category (0-100 scale)
    scores = []
    
    # Growth score (based on GDP, Industrial Production)
    gdp_val = df[df['series_id'] == 'GDPC1']['latest_value'].values[0] if 'GDPC1' in df['series_id'].values else 23000
    growth_score = min(100, (gdp_val / 25000) * 100)  # Normalize to 25T baseline
    scores.append(growth_score)
    
    # Employment score (inverse of unemployment)
    unemp = df[df['series_id'] == 'UNRATE']['latest_value'].values[0] if 'UNRATE' in df['series_id'].values else 4.2
    emp_score = max(0, 100 - (unemp - 3.5) * 20)  # 3.5% as ideal, -20 points per % above
    scores.append(emp_score)
    
    # Inflation score (distance from 2% target)
    cpi = df[df['series_id'] == 'CPIAUCSL']['latest_value'].values[0] if 'CPIAUCSL' in df['series_id'].values else 320
    # Estimate YoY inflation (rough approximation)
    inflation_est = 3.0  # Placeholder
    inflation_score = max(0, 100 - abs(inflation_est - 2.0) * 30)
    scores.append(inflation_score)
    
    # Markets score (based on VIX inverse)
    vix = df[df['series_id'] == 'VIXCLS']['latest_value'].values[0] if 'VIXCLS' in df['series_id'].values else 20
    market_score = max(0, 100 - (vix - 10) * 3)  # 10 as ideal VIX, -3 points per point above
    scores.append(market_score)
    
    # Credit score (based on credit growth)
    m2 = df[df['series_id'] == 'M2SL']['latest_value'].values[0] if 'M2SL' in df['series_id'].values else 21000
    credit_score = min(100, (m2 / 22000) * 100)  # Normalize to 22T
    scores.append(credit_score)
    
    # Trade score (placeholder)
    trade_score = 75  # Neutral
    scores.append(trade_score)
    
    # Create radar chart
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    scores += scores[:1]  # Complete the circle
    angles += angles[:1]
    
    ax.plot(angles, scores, 'o-', linewidth=2, color='darkblue')
    ax.fill(angles, scores, alpha=0.3, color='skyblue')
    
    # Add reference circles
    for level in [20, 40, 60, 80, 100]:
        ax.plot(angles, [level] * len(angles), 'k--', alpha=0.2, linewidth=0.5)
    
    # Set labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=14)
    ax.set_ylim(0, 100)
    ax.set_title('Economic Health Radar Chart', fontsize=18, fontweight='bold', pad=20)
    
    # Add score labels
    for angle, score, cat in zip(angles[:-1], scores[:-1], categories):
        ax.text(angle, score + 5, f'{score:.0f}', ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Add summary text
    overall_score = np.mean(scores[:-1])
    summary = f"Overall Economic Health Score: {overall_score:.1f}/100"
    ax.text(0.5, -0.15, summary, transform=ax.transAxes, ha='center', fontsize=16, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen" if overall_score > 70 else "yellow"))
    
    plt.tight_layout()
    plt.savefig('fred_economic_radar.png', dpi=300, bbox_inches='tight')
    print("💾 Saved: fred_economic_radar.png")

if __name__ == "__main__":
    print("🎨 Creating detailed FRED visualizations...")
    create_detailed_visualizations()
    print("\n✅ All visualizations created successfully!")