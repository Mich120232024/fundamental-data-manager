#!/usr/bin/env python3
"""
FRED Historical Time Series Analysis - Military Grade
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Professional-level historical analysis and quantitative analytics framework
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fredapi import Fred
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
warnings.filterwarnings('ignore')

# Load environment
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Initialize FRED
FRED_API_KEY = os.getenv('FRED_API_KEY')
fred = Fred(api_key=FRED_API_KEY)

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def get_historical_data():
    """Retrieve comprehensive historical data for key series"""
    
    print("🎖️ MILITARY-GRADE FRED HISTORICAL DATA RETRIEVAL")
    print("="*60)
    
    # Define critical series for professional analysis
    CRITICAL_SERIES = {
        # Core Economic Indicators
        'GDPC1': 'Real GDP',
        'UNRATE': 'Unemployment Rate',
        'CPIAUCSL': 'CPI All Items',
        'CPILFESL': 'Core CPI',
        'PCEPI': 'PCE Price Index',
        'PCEPILFE': 'Core PCE',
        
        # Monetary Policy
        'FEDFUNDS': 'Fed Funds Rate',
        'DGS2': '2-Year Treasury',
        'DGS10': '10-Year Treasury',
        'T10Y2Y': '10Y-2Y Spread',
        'DFEDTARU': 'Fed Target Upper',
        
        # Financial Markets
        'SP500': 'S&P 500',
        'VIXCLS': 'VIX',
        'DEXUSEU': 'EUR/USD',
        'DCOILWTICO': 'WTI Oil',
        
        # Credit & Money
        'M2SL': 'M2 Money Supply',
        'TOTBKCR': 'Bank Credit',
        'BUSLOANS': 'Business Loans',
        
        # Leading Indicators
        'ICSA': 'Initial Claims',
        'HOUST': 'Housing Starts',
        'INDPRO': 'Industrial Production',
        'UMCSENT': 'Consumer Sentiment',
        'PERMIT': 'Building Permits',
        
        # Business Cycle
        'USREC': 'Recession Indicator',
        'SAHM': 'Sahm Rule',
        'NFCI': 'Financial Conditions'
    }
    
    # Get historical data (10 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*10)
    
    historical_data = {}
    failed_series = []
    
    for series_id, name in CRITICAL_SERIES.items():
        try:
            print(f"📊 Retrieving {series_id} ({name})...", end='')
            data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
            
            if data is not None and len(data) > 0:
                historical_data[series_id] = {
                    'data': data,
                    'name': name,
                    'count': len(data),
                    'start': data.index[0],
                    'end': data.index[-1],
                    'latest': data.iloc[-1]
                }
                print(f" ✓ {len(data)} observations")
            else:
                failed_series.append(series_id)
                print(" ❌ No data")
                
        except Exception as e:
            failed_series.append(series_id)
            print(f" ❌ Error: {str(e)[:30]}")
    
    print(f"\n✅ Successfully retrieved {len(historical_data)} series")
    if failed_series:
        print(f"⚠️  Failed: {', '.join(failed_series)}")
    
    return historical_data

def create_professional_analysis(historical_data):
    """Create military-grade analytical visualizations"""
    
    # Create comprehensive figure
    fig = plt.figure(figsize=(24, 30))
    
    # 1. Economic Cycle Analysis
    ax1 = plt.subplot(6, 2, 1)
    if 'GDPC1' in historical_data and 'UNRATE' in historical_data:
        gdp_data = historical_data['GDPC1']['data']
        gdp_pct_change = gdp_data.pct_change(4) * 100  # YoY %
        
        ax1_twin = ax1.twinx()
        ax1.plot(gdp_pct_change.index, gdp_pct_change.values, 'b-', linewidth=2, label='GDP Growth YoY%')
        ax1_twin.plot(historical_data['UNRATE']['data'].index, 
                     historical_data['UNRATE']['data'].values, 'r-', linewidth=2, label='Unemployment %')
        
        # Add recession bars if available
        if 'USREC' in historical_data:
            recession = historical_data['USREC']['data']
            ax1.fill_between(recession.index, 0, 1, where=recession==1, 
                           alpha=0.3, color='gray', transform=ax1.get_xaxis_transform())
        
        ax1.set_title('Economic Cycle: GDP Growth vs Unemployment', fontsize=14, fontweight='bold')
        ax1.set_ylabel('GDP Growth %', color='b')
        ax1_twin.set_ylabel('Unemployment %', color='r')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        ax1_twin.legend(loc='upper right')
    
    # 2. Inflation Dynamics
    ax2 = plt.subplot(6, 2, 2)
    if 'CPIAUCSL' in historical_data and 'PCEPILFE' in historical_data:
        cpi = historical_data['CPIAUCSL']['data'].pct_change(12) * 100
        core_pce = historical_data['PCEPILFE']['data'].pct_change(12) * 100
        
        ax2.plot(cpi.index, cpi.values, 'r-', linewidth=2, label='CPI YoY%')
        ax2.plot(core_pce.index, core_pce.values, 'b-', linewidth=2, label='Core PCE YoY%')
        ax2.axhline(y=2, color='g', linestyle='--', alpha=0.5, label='Fed Target')
        
        ax2.set_title('Inflation Dynamics: CPI vs Core PCE', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Inflation Rate %')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # 3. Yield Curve Evolution
    ax3 = plt.subplot(6, 2, 3)
    if 'T10Y2Y' in historical_data and 'FEDFUNDS' in historical_data:
        spread = historical_data['T10Y2Y']['data']
        fed_funds = historical_data['FEDFUNDS']['data']
        
        ax3_twin = ax3.twinx()
        ax3.plot(spread.index, spread.values, 'purple', linewidth=2, label='10Y-2Y Spread')
        ax3.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax3_twin.plot(fed_funds.index, fed_funds.values, 'orange', linewidth=2, label='Fed Funds')
        
        # Highlight inversions
        ax3.fill_between(spread.index, spread.values, 0, where=spread<0, 
                        alpha=0.3, color='red', label='Inversion')
        
        ax3.set_title('Yield Curve & Monetary Policy', fontsize=14, fontweight='bold')
        ax3.set_ylabel('10Y-2Y Spread %', color='purple')
        ax3_twin.set_ylabel('Fed Funds %', color='orange')
        ax3.legend(loc='upper left')
        ax3_twin.legend(loc='upper right')
        ax3.grid(True, alpha=0.3)
    
    # 4. Market Risk Indicators
    ax4 = plt.subplot(6, 2, 4)
    if 'SP500' in historical_data and 'VIXCLS' in historical_data:
        sp500 = historical_data['SP500']['data']
        vix = historical_data['VIXCLS']['data']
        
        # Calculate rolling correlation
        sp500_returns = sp500.pct_change()
        
        ax4_twin = ax4.twinx()
        ax4.plot(sp500.index, sp500.values, 'green', linewidth=2, label='S&P 500')
        ax4_twin.plot(vix.index, vix.values, 'red', linewidth=2, label='VIX')
        
        # Highlight high volatility periods
        ax4_twin.fill_between(vix.index, vix.values, 20, where=vix>20, 
                             alpha=0.2, color='red', label='High Vol')
        
        ax4.set_title('Market Risk: S&P 500 vs VIX', fontsize=14, fontweight='bold')
        ax4.set_ylabel('S&P 500', color='green')
        ax4_twin.set_ylabel('VIX', color='red')
        ax4.legend(loc='upper left')
        ax4_twin.legend(loc='upper right')
        ax4.grid(True, alpha=0.3)
    
    # 5. Credit Cycle Analysis
    ax5 = plt.subplot(6, 2, 5)
    if 'M2SL' in historical_data and 'BUSLOANS' in historical_data:
        m2_growth = historical_data['M2SL']['data'].pct_change(12) * 100
        loans_growth = historical_data['BUSLOANS']['data'].pct_change(12) * 100
        
        ax5.plot(m2_growth.index, m2_growth.values, 'blue', linewidth=2, label='M2 Growth YoY%')
        ax5.plot(loans_growth.index, loans_growth.values, 'green', linewidth=2, label='Business Loans YoY%')
        
        ax5.set_title('Credit Cycle: Money Supply & Lending', fontsize=14, fontweight='bold')
        ax5.set_ylabel('Growth Rate %')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
    
    # 6. Leading Indicators Dashboard
    ax6 = plt.subplot(6, 2, 6)
    leading_indicators = ['ICSA', 'PERMIT', 'UMCSENT']
    available_leading = [ind for ind in leading_indicators if ind in historical_data]
    
    if available_leading:
        for i, indicator in enumerate(available_leading):
            data = historical_data[indicator]['data']
            # Normalize to 100 at start
            normalized = (data / data.iloc[0]) * 100
            ax6.plot(normalized.index, normalized.values, linewidth=2, 
                    label=historical_data[indicator]['name'])
        
        ax6.set_title('Leading Indicators (Normalized)', fontsize=14, fontweight='bold')
        ax6.set_ylabel('Index (Start = 100)')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
    
    # 7. Rolling Correlations Matrix
    ax7 = plt.subplot(6, 2, 7)
    # Calculate rolling correlations for key pairs
    if 'GDPC1' in historical_data and 'SP500' in historical_data:
        gdp_returns = historical_data['GDPC1']['data'].pct_change(4)
        sp500_returns = historical_data['SP500']['data'].pct_change(252)
        
        # Align data
        aligned_data = pd.DataFrame({
            'GDP': gdp_returns,
            'SP500': sp500_returns
        }).dropna()
        
        if len(aligned_data) > 252:
            rolling_corr = aligned_data['GDP'].rolling(window=252).corr(aligned_data['SP500'])
            ax7.plot(rolling_corr.index, rolling_corr.values, linewidth=2)
            ax7.set_title('Rolling 1Y Correlation: GDP vs S&P 500', fontsize=14, fontweight='bold')
            ax7.set_ylabel('Correlation')
            ax7.axhline(y=0, color='red', linestyle='--', alpha=0.5)
            ax7.grid(True, alpha=0.3)
    
    # 8. Regime Analysis
    ax8 = plt.subplot(6, 2, 8)
    if 'VIXCLS' in historical_data and 'FEDFUNDS' in historical_data:
        vix = historical_data['VIXCLS']['data']
        fed = historical_data['FEDFUNDS']['data']
        
        # Define regimes
        regime_data = pd.DataFrame({
            'VIX': vix,
            'FedFunds': fed
        }).dropna()
        
        # Create regime scatter
        scatter = ax8.scatter(regime_data['FedFunds'], regime_data['VIX'], 
                            c=regime_data.index, cmap='viridis', alpha=0.6)
        
        # Add regime boundaries
        ax8.axhline(y=20, color='red', linestyle='--', alpha=0.5, label='VIX=20')
        ax8.axvline(x=2, color='blue', linestyle='--', alpha=0.5, label='FF=2%')
        
        ax8.set_xlabel('Fed Funds Rate %')
        ax8.set_ylabel('VIX')
        ax8.set_title('Market Regime Analysis', fontsize=14, fontweight='bold')
        ax8.legend()
        ax8.grid(True, alpha=0.3)
        
        # Add colorbar for time
        cbar = plt.colorbar(scatter, ax=ax8)
        cbar.set_label('Time')
    
    # 9. Momentum Indicators
    ax9 = plt.subplot(6, 2, 9)
    if 'INDPRO' in historical_data:
        indpro = historical_data['INDPRO']['data']
        
        # Calculate momentum indicators
        mom_3m = indpro.pct_change(3) * 100
        mom_12m = indpro.pct_change(12) * 100
        
        ax9.plot(mom_3m.index, mom_3m.values, 'blue', linewidth=1, alpha=0.7, label='3M Momentum')
        ax9.plot(mom_12m.index, mom_12m.values, 'red', linewidth=2, label='12M Momentum')
        ax9.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Add momentum regime shading
        ax9.fill_between(mom_12m.index, 0, mom_12m.values, where=mom_12m>0, 
                        alpha=0.2, color='green', label='Expansion')
        ax9.fill_between(mom_12m.index, 0, mom_12m.values, where=mom_12m<0, 
                        alpha=0.2, color='red', label='Contraction')
        
        ax9.set_title('Industrial Production Momentum', fontsize=14, fontweight='bold')
        ax9.set_ylabel('Growth Rate %')
        ax9.legend()
        ax9.grid(True, alpha=0.3)
    
    # 10. Risk-On/Risk-Off Indicator
    ax10 = plt.subplot(6, 2, 10)
    if 'DEXUSEU' in historical_data and 'DCOILWTICO' in historical_data:
        eur = historical_data['DEXUSEU']['data']
        oil = historical_data['DCOILWTICO']['data']
        
        # Calculate risk indicator
        eur_ma = eur.rolling(window=50).mean()
        oil_ma = oil.rolling(window=50).mean()
        
        risk_on = ((eur > eur_ma) & (oil > oil_ma)).astype(int)
        risk_smooth = risk_on.rolling(window=20).mean()
        
        ax10.fill_between(risk_smooth.index, 0, risk_smooth.values, 
                         where=risk_smooth>0.5, alpha=0.3, color='green', label='Risk On')
        ax10.fill_between(risk_smooth.index, 0, risk_smooth.values, 
                         where=risk_smooth<=0.5, alpha=0.3, color='red', label='Risk Off')
        ax10.plot(risk_smooth.index, risk_smooth.values, 'black', linewidth=2)
        
        ax10.set_title('Risk Sentiment Indicator', fontsize=14, fontweight='bold')
        ax10.set_ylabel('Risk Score (0-1)')
        ax10.set_ylim(0, 1)
        ax10.legend()
        ax10.grid(True, alpha=0.3)
    
    # 11. Economic Surprise Index
    ax11 = plt.subplot(6, 2, 11)
    # Create synthetic surprise index from multiple indicators
    surprise_components = ['GDPC1', 'CPIAUCSL', 'UNRATE', 'INDPRO']
    available_components = [comp for comp in surprise_components if comp in historical_data]
    
    if len(available_components) >= 2:
        surprise_data = pd.DataFrame()
        for comp in available_components:
            data = historical_data[comp]['data']
            # Calculate z-score of changes
            changes = data.pct_change(periods=4).dropna()
            z_score = (changes - changes.rolling(window=20).mean()) / changes.rolling(window=20).std()
            surprise_data[comp] = z_score
        
        # Composite surprise index
        surprise_index = surprise_data.mean(axis=1)
        
        ax11.plot(surprise_index.index, surprise_index.values, 'purple', linewidth=2)
        ax11.fill_between(surprise_index.index, 0, surprise_index.values, 
                         where=surprise_index>0, alpha=0.3, color='green')
        ax11.fill_between(surprise_index.index, 0, surprise_index.values, 
                         where=surprise_index<0, alpha=0.3, color='red')
        
        ax11.set_title('Economic Surprise Index (Composite)', fontsize=14, fontweight='bold')
        ax11.set_ylabel('Z-Score')
        ax11.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax11.grid(True, alpha=0.3)
    
    # 12. Quantitative Strategy Performance
    ax12 = plt.subplot(6, 2, 12)
    # Create a simple momentum strategy backtest
    if 'SP500' in historical_data:
        sp500 = historical_data['SP500']['data']
        returns = sp500.pct_change()
        
        # Simple momentum signal
        sma_20 = sp500.rolling(window=20).mean()
        sma_50 = sp500.rolling(window=50).mean()
        signal = (sma_20 > sma_50).astype(int)
        
        # Calculate strategy returns
        strategy_returns = returns * signal.shift(1)
        
        # Cumulative returns
        buy_hold = (1 + returns).cumprod()
        strategy = (1 + strategy_returns).cumprod()
        
        ax12.plot(buy_hold.index, buy_hold.values, 'blue', linewidth=2, label='Buy & Hold')
        ax12.plot(strategy.index, strategy.values, 'red', linewidth=2, label='Momentum Strategy')
        
        ax12.set_title('Simple Momentum Strategy Backtest', fontsize=14, fontweight='bold')
        ax12.set_ylabel('Cumulative Return')
        ax12.legend()
        ax12.grid(True, alpha=0.3)
    
    plt.suptitle('MILITARY-GRADE QUANTITATIVE ANALYSIS DASHBOARD', fontsize=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig('fred_military_grade_analysis.png', dpi=300, bbox_inches='tight')
    print("💾 Saved: fred_military_grade_analysis.png")
    
    return fig

def generate_quant_recommendations():
    """Generate professional quantitative analytics recommendations"""
    
    recommendations = """
🎖️ MILITARY-GRADE QUANTITATIVE ANALYTICS RECOMMENDATIONS

1. ADVANCED TIME SERIES MODELS
   • Vector Autoregression (VAR) - Multi-variable forecasting
   • VECM - Cointegration analysis for long-run relationships
   • State-Space Models - Kalman filtering for noisy data
   • GARCH Family - Volatility forecasting (EGARCH, GJR-GARCH)
   • Regime-Switching Models - Markov regime detection

2. MACHINE LEARNING APPLICATIONS
   • Random Forests - Feature importance for macro drivers
   • XGBoost - Non-linear pattern detection
   • LSTM Networks - Sequential prediction with memory
   • Autoencoders - Anomaly detection in economic data
   • Reinforcement Learning - Dynamic portfolio optimization

3. RISK MANAGEMENT FRAMEWORKS
   • Value at Risk (VaR) - Historical, Monte Carlo, EVT
   • Expected Shortfall - Tail risk measurement
   • Stress Testing - Scenario analysis framework
   • Copula Models - Dependency structure modeling
   • Dynamic Hedging - Delta-neutral strategies

4. PORTFOLIO OPTIMIZATION
   • Black-Litterman - Bayesian asset allocation
   • Risk Parity - Equal risk contribution
   • Mean-CVaR Optimization - Downside risk focus
   • Factor Models - Multi-factor attribution
   • Kelly Criterion - Optimal position sizing

5. NOWCASTING SYSTEMS
   • Mixed-Frequency Models - MIDAS, MF-VAR
   • Dynamic Factor Models - Extract common trends
   • Bridge Equations - High to low frequency mapping
   • Machine Learning Nowcasts - Real-time GDP tracking
   • Sentiment Analysis - News flow quantification

6. MARKET MICROSTRUCTURE
   • Order Flow Analysis - Volume/price dynamics
   • Market Impact Models - Transaction cost analysis
   • High-Frequency Indicators - Tick data analysis
   • Liquidity Measures - Bid-ask spread decomposition
   • Price Discovery - Lead-lag relationships

7. CAUSAL INFERENCE
   • Granger Causality - Temporal precedence
   • Instrumental Variables - Endogeneity correction
   • Difference-in-Differences - Policy impact analysis
   • Synthetic Control - Counterfactual analysis
   • Regression Discontinuity - Threshold effects

8. BACKTESTING INFRASTRUCTURE
   • Walk-Forward Analysis - Out-of-sample validation
   • Monte Carlo Permutation - Statistical significance
   • Bootstrap Methods - Confidence intervals
   • Transaction Cost Modeling - Realistic P&L
   • Regime-Aware Backtesting - Conditional performance

9. REAL-TIME MONITORING
   • Automated Anomaly Detection - Statistical process control
   • Dashboard Systems - KPI tracking
   • Alert Mechanisms - Threshold breaches
   • Performance Attribution - Return decomposition
   • Risk Decomposition - Factor contributions

10. RESEARCH INFRASTRUCTURE
    • Reproducible Research - Version control, documentation
    • Parallel Computing - Large-scale simulations
    • Database Architecture - Time-series optimization
    • API Integration - Real-time data feeds
    • Automated Reporting - LaTeX/Markdown generation
"""
    
    with open('fred_quant_recommendations.txt', 'w') as f:
        f.write(recommendations)
    
    print("\n" + recommendations)
    
    return recommendations

def main():
    """Execute military-grade analysis"""
    
    print("🎖️ INITIATING MILITARY-GRADE QUANTITATIVE ANALYSIS")
    print("="*60)
    
    # Get historical data
    historical_data = get_historical_data()
    
    # Create professional analysis
    print("\n📊 Creating professional visualizations...")
    create_professional_analysis(historical_data)
    
    # Generate recommendations
    print("\n📋 Generating quantitative recommendations...")
    generate_quant_recommendations()
    
    # Save data for further analysis
    print("\n💾 Saving historical data...")
    
    # Create combined DataFrame
    combined_data = pd.DataFrame()
    for series_id, info in historical_data.items():
        df = pd.DataFrame(info['data'])
        df.columns = [series_id]
        if combined_data.empty:
            combined_data = df
        else:
            combined_data = combined_data.join(df, how='outer')
    
    combined_data.to_csv('fred_historical_data_10y.csv')
    print(f"✅ Saved {len(combined_data)} observations across {len(combined_data.columns)} series")
    
    print("\n🎖️ MILITARY-GRADE ANALYSIS COMPLETE")
    print("Files created:")
    print("   - fred_military_grade_analysis.png")
    print("   - fred_quant_recommendations.txt")
    print("   - fred_historical_data_10y.csv")

if __name__ == "__main__":
    main()