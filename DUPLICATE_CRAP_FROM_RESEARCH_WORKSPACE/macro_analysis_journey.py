#!/usr/bin/env python3
"""
COMPLETE MACRO ECONOMIC ANALYSIS JOURNEY
From Raw Data → Fully Integrated Model
Author: HEAD_OF_RESEARCH
Date: 2025-06-22
"""

import pandas as pd
import numpy as np
import networkx as nx
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

print("🚀 MACRO ECONOMIC ANALYSIS JOURNEY - SAMPLE DATA")
print("="*60)

# ============================================
# STEP 1: CREATE SAMPLE DATA
# ============================================
print("\n📊 STEP 1: Creating Sample Economic Data...")

# 1.1 Create date range (3 years of daily data)
dates = pd.date_range(start='2022-01-01', end='2024-12-31', freq='D')
n_days = len(dates)

# 1.2 Create countries and commodities
countries = ['USA', 'China', 'Germany', 'Japan', 'UK', 'India', 'Brazil', 'Canada', 'Australia', 'Mexico']
commodities = ['Oil', 'Gold', 'Wheat', 'Copper', 'Natural_Gas']

# 1.3 Generate Trade Flow Data
print("Creating trade flow data...")
trade_records = []
for date in dates[::7]:  # Weekly trade data
    for exporter in countries:
        for importer in countries:
            if exporter != importer:
                # Create realistic trade patterns
                base_trade = np.random.uniform(100, 1000)
                if (exporter == 'China' and importer == 'USA') or (exporter == 'USA' and importer == 'China'):
                    base_trade *= 5  # Major trade relationship
                
                # Add seasonality and trend
                seasonal = np.sin(2 * np.pi * date.dayofyear / 365) * 0.2
                trend = (date - dates[0]).days / 1000 * 0.1
                noise = np.random.normal(0, 0.1)
                
                trade_value = base_trade * (1 + seasonal + trend + noise)
                
                trade_records.append({
                    'date': date,
                    'exporter': exporter,
                    'importer': importer,
                    'trade_value': max(0, trade_value),
                    'commodity': np.random.choice(commodities)
                })

trade_data = pd.DataFrame(trade_records)
print(f"✓ Created {len(trade_data):,} trade records")

# 1.4 Generate Commodity Price Data
print("Creating commodity price data...")
commodity_prices = pd.DataFrame({'date': dates})

for commodity in commodities:
    # Base prices
    base_prices = {
        'Oil': 80,
        'Gold': 1800,
        'Wheat': 300,
        'Copper': 9000,
        'Natural_Gas': 3
    }
    
    base = base_prices[commodity]
    prices = [base]
    
    # Generate realistic price movements
    for i in range(1, n_days):
        # Mean reversion with random walk
        change = -0.001 * (prices[-1] - base) + np.random.normal(0, base * 0.02)
        
        # Add occasional shocks
        if np.random.random() < 0.01:  # 1% chance of shock
            change += np.random.normal(0, base * 0.1)
        
        new_price = prices[-1] + change
        prices.append(max(new_price, base * 0.5))  # Floor at 50% of base
    
    commodity_prices[f'{commodity}_price'] = prices

print(f"✓ Created price data for {len(commodities)} commodities")

# 1.5 Generate Interest Rate Data
print("Creating interest rate data...")
rate_data = []
for country in countries:
    base_rate = np.random.uniform(0.5, 5.0)  # Base rate between 0.5% and 5%
    
    for i, date in enumerate(dates[::30]):  # Monthly rate decisions
        # Central banks adjust rates slowly
        if i > 0:
            # Small adjustments
            adjustment = np.random.choice([-0.25, 0, 0, 0, 0.25], p=[0.1, 0.7, 0.1, 0.05, 0.05])
            base_rate = np.clip(base_rate + adjustment, 0, 10)
        
        rate_data.append({
            'date': date,
            'country': country,
            'rate': base_rate
        })

interest_rates = pd.DataFrame(rate_data)
print(f"✓ Created interest rate data for {len(countries)} countries")

# 1.6 Generate GDP Data
print("Creating GDP data...")
gdp_data = []
gdp_base = {
    'USA': 25000, 'China': 17000, 'Japan': 4200, 'Germany': 4000,
    'India': 3700, 'UK': 3100, 'Brazil': 2100, 'Canada': 2100,
    'Australia': 1600, 'Mexico': 1400
}

for country in countries:
    base_gdp = gdp_base[country]
    
    for i, date in enumerate(pd.date_range(start='2022-01-01', end='2024-12-31', freq='Q')):
        # GDP grows slowly with some volatility
        growth_rate = np.random.normal(0.02, 0.01)  # 2% average annual growth
        quarter_gdp = base_gdp * (1 + growth_rate) ** (i / 4)
        
        gdp_data.append({
            'date': date,
            'country': country,
            'gdp': quarter_gdp,
            'gdp_growth': growth_rate * 4  # Annualized
        })

gdp_data = pd.DataFrame(gdp_data)
print(f"✓ Created GDP data for {len(countries)} countries")

# ============================================
# STEP 2: DATA EXPLORATION & VISUALIZATION
# ============================================
print("\n🔍 STEP 2: Exploring the Data...")

# 2.1 Summary statistics
print("\nTrade Data Summary:")
print(f"Date range: {trade_data['date'].min()} to {trade_data['date'].max()}")
print(f"Total trade volume: ${trade_data['trade_value'].sum():,.0f}M")
print(f"Average trade per transaction: ${trade_data['trade_value'].mean():,.0f}M")

print("\nTop 5 Trading Relationships:")
top_trades = trade_data.groupby(['exporter', 'importer'])['trade_value'].sum().sort_values(ascending=False).head()
for (exp, imp), value in top_trades.items():
    print(f"  {exp} → {imp}: ${value:,.0f}M")

# 2.2 Visualize commodity prices
plt.figure(figsize=(12, 6))
for commodity in commodities:
    plt.plot(commodity_prices['date'], commodity_prices[f'{commodity}_price'], 
             label=commodity, alpha=0.7)
plt.title('Commodity Price Evolution')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/Users/mikaeleage/Research & Analytics Services/Research Workspace/commodity_prices.png')
plt.close()
print("✓ Saved commodity price chart")

# ============================================
# STEP 3: NETWORK ANALYSIS
# ============================================
print("\n🌐 STEP 3: Building Trade Network...")

# 3.1 Create trade network
# Aggregate trade values
trade_edges = trade_data.groupby(['exporter', 'importer'])['trade_value'].sum().reset_index()

# Create directed graph
G = nx.from_pandas_edgelist(
    trade_edges,
    source='exporter',
    target='importer',
    edge_attr='trade_value',
    create_using=nx.DiGraph()
)

print(f"Network Statistics:")
print(f"  Nodes (countries): {G.number_of_nodes()}")
print(f"  Edges (trade relationships): {G.number_of_edges()}")
print(f"  Network density: {nx.density(G):.3f}")

# 3.2 Calculate centrality measures
print("\nCalculating network metrics...")
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G, weight='trade_value')
pagerank = nx.pagerank(G, weight='trade_value')
clustering = nx.clustering(G)

# 3.3 Identify critical nodes
centrality_df = pd.DataFrame({
    'country': list(G.nodes()),
    'degree_centrality': [degree_centrality[node] for node in G.nodes()],
    'betweenness_centrality': [betweenness_centrality[node] for node in G.nodes()],
    'pagerank': [pagerank[node] for node in G.nodes()],
    'clustering': [clustering[node] for node in G.nodes()]
})

print("\nMost Central Countries (by PageRank):")
top_countries = centrality_df.sort_values('pagerank', ascending=False).head()
print(top_countries[['country', 'pagerank', 'betweenness_centrality']])

# 3.4 Visualize network
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=2, iterations=50)

# Node sizes based on PageRank
node_sizes = [pagerank[node] * 10000 for node in G.nodes()]

# Edge widths based on trade volume
edge_widths = [G[u][v]['trade_value'] / 1000 for u, v in G.edges()]

nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightblue', alpha=0.7)
nx.draw_networkx_labels(G, pos, font_size=10)
nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.3, arrows=True)

plt.title('Global Trade Network (Node size = PageRank importance)')
plt.axis('off')
plt.tight_layout()
plt.savefig('/Users/mikaeleage/Research & Analytics Services/Research Workspace/trade_network.png')
plt.close()
print("✓ Saved trade network visualization")

# ============================================
# STEP 4: CUSTOM ECONOMIC INDICATORS
# ============================================
print("\n📈 STEP 4: Creating Custom Economic Indicators...")

# 4.1 Supply Chain Stress Index
def calculate_supply_chain_stress(trade_df, commodity_prices_df):
    """Calculate supply chain stress based on trade volatility and commodity price spikes"""
    
    # Trade flow volatility
    daily_trade = trade_df.groupby('date')['trade_value'].sum()
    trade_volatility = daily_trade.pct_change().rolling(30).std()
    
    # Commodity price volatility (average across all commodities)
    price_cols = [col for col in commodity_prices_df.columns if col.endswith('_price')]
    price_volatility = commodity_prices_df[price_cols].pct_change().rolling(30).std().mean(axis=1)
    
    # Combine into stress index
    stress_index = pd.DataFrame({
        'date': commodity_prices_df['date'],
        'trade_volatility': trade_volatility.reindex(commodity_prices_df['date']).fillna(method='ffill'),
        'price_volatility': price_volatility
    })
    
    # Normalize and combine (handle NaN values)
    trade_vol_norm = stress_index['trade_volatility'] / stress_index['trade_volatility'].mean()
    price_vol_norm = stress_index['price_volatility'] / stress_index['price_volatility'].mean()
    
    # Fill NaN with 1.0 (neutral stress)
    trade_vol_norm = trade_vol_norm.fillna(1.0)
    price_vol_norm = price_vol_norm.fillna(1.0)
    
    stress_index['stress'] = 0.5 * trade_vol_norm + 0.5 * price_vol_norm
    
    return stress_index

stress_index = calculate_supply_chain_stress(trade_data, commodity_prices)
print("✓ Created Supply Chain Stress Index")

# 4.2 Economic Momentum Indicator
def calculate_economic_momentum(gdp_df, rates_df):
    """Composite momentum indicator combining GDP growth and interest rate changes"""
    
    momentum_data = []
    
    for country in countries:
        # GDP momentum (year-over-year growth)
        country_gdp = gdp_df[gdp_df['country'] == country].sort_values('date')
        gdp_momentum = country_gdp['gdp_growth'].rolling(4).mean()  # 4-quarter average
        
        # Rate momentum (inverted - falling rates = positive momentum)
        country_rates = rates_df[rates_df['country'] == country].sort_values('date')
        rate_changes = -country_rates['rate'].diff()
        
        # Combine
        for i, date in enumerate(country_gdp['date']):
            momentum_data.append({
                'date': date,
                'country': country,
                'gdp_momentum': gdp_momentum.iloc[i] if i < len(gdp_momentum) else 0,
                'rate_momentum': rate_changes.iloc[i//3] if i//3 < len(rate_changes) else 0,
                'combined_momentum': (gdp_momentum.iloc[i] if i < len(gdp_momentum) else 0) + 
                                   (rate_changes.iloc[i//3] if i//3 < len(rate_changes) else 0)
            })
    
    return pd.DataFrame(momentum_data)

momentum_index = calculate_economic_momentum(gdp_data, interest_rates)
print("✓ Created Economic Momentum Indicator")

# 4.3 Trade Concentration Index (Herfindahl-Hirschman)
def calculate_trade_concentration(trade_df):
    """Calculate how concentrated trade is among countries"""
    
    concentration_data = []
    
    for date in trade_df['date'].unique():
        date_trades = trade_df[trade_df['date'] == date]
        
        # Export concentration
        export_shares = date_trades.groupby('exporter')['trade_value'].sum()
        export_shares = export_shares / export_shares.sum()
        export_hhi = (export_shares ** 2).sum()
        
        # Import concentration
        import_shares = date_trades.groupby('importer')['trade_value'].sum()
        import_shares = import_shares / import_shares.sum()
        import_hhi = (import_shares ** 2).sum()
        
        concentration_data.append({
            'date': date,
            'export_concentration': export_hhi,
            'import_concentration': import_hhi,
            'avg_concentration': (export_hhi + import_hhi) / 2
        })
    
    return pd.DataFrame(concentration_data)

concentration_index = calculate_trade_concentration(trade_data)
print("✓ Created Trade Concentration Index")

# Visualize custom indicators
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Supply Chain Stress
axes[0].plot(stress_index['date'], stress_index['stress'], color='red', alpha=0.7)
axes[0].fill_between(stress_index['date'], stress_index['stress'], alpha=0.3, color='red')
axes[0].set_title('Supply Chain Stress Index')
axes[0].set_ylabel('Stress Level')
axes[0].grid(True, alpha=0.3)

# Economic Momentum (USA)
usa_momentum = momentum_index[momentum_index['country'] == 'USA']
axes[1].plot(usa_momentum['date'], usa_momentum['combined_momentum'], color='blue', alpha=0.7)
axes[1].set_title('Economic Momentum - USA')
axes[1].set_ylabel('Momentum')
axes[1].grid(True, alpha=0.3)

# Trade Concentration
axes[2].plot(concentration_index['date'], concentration_index['avg_concentration'], color='green', alpha=0.7)
axes[2].set_title('Trade Concentration Index (Lower = More Diversified)')
axes[2].set_ylabel('HHI')
axes[2].set_xlabel('Date')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/mikaeleage/Research & Analytics Services/Research Workspace/custom_indicators.png')
plt.close()
print("✓ Saved custom indicators visualization")

# ============================================
# STEP 5: TIME SERIES FORECASTING
# ============================================
print("\n🔮 STEP 5: Forecasting with Prophet...")

# Prepare data for Prophet
prophet_data = pd.DataFrame({
    'ds': stress_index['date'],
    'y': stress_index['stress']
})

# Remove NaN values
prophet_data = prophet_data.dropna()

# Ensure we have enough data
print(f"Prophet data shape: {prophet_data.shape}")
if len(prophet_data) < 10:
    # Fill with more realistic data
    prophet_data['y'] = prophet_data['y'].fillna(1.0)

# Add external regressors (oil price and USA interest rate)
prophet_data['oil_price'] = commodity_prices['Oil_price'].values[:len(prophet_data)]
usa_rates = interest_rates[interest_rates['country'] == 'USA'].set_index('date')['rate']
prophet_data['usa_rate'] = usa_rates.reindex(prophet_data['ds']).fillna(method='ffill').values

# Create and fit model
model = Prophet(
    changepoint_prior_scale=0.05,
    seasonality_mode='multiplicative',
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False
)

# Add regressors
model.add_regressor('oil_price')
model.add_regressor('usa_rate')

print("Fitting Prophet model...")
model.fit(prophet_data)

# Make future predictions
future = model.make_future_dataframe(periods=90)  # 90 days forecast

# For future periods, assume oil price and rates stay constant
future['oil_price'] = prophet_data['oil_price'].iloc[-1]
future['usa_rate'] = prophet_data['usa_rate'].iloc[-1]

# Generate forecast
forecast = model.predict(future)

# Visualize forecast
plt.figure(figsize=(12, 6))
plt.plot(prophet_data['ds'], prophet_data['y'], label='Historical', alpha=0.7)
plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', color='red')
plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], 
                 alpha=0.3, color='red', label='Confidence Interval')
plt.axvline(x=prophet_data['ds'].iloc[-1], color='black', linestyle='--', alpha=0.5)
plt.title('Supply Chain Stress Forecast (90 days)')
plt.xlabel('Date')
plt.ylabel('Stress Index')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/Users/mikaeleage/Research & Analytics Services/Research Workspace/stress_forecast.png')
plt.close()
print("✓ Created 90-day stress forecast")

# ============================================
# STEP 6: MACHINE LEARNING - CRISIS DETECTION
# ============================================
print("\n🤖 STEP 6: Building Crisis Detection Model...")

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
# import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier

# Create features for ML
ml_features = pd.DataFrame(index=stress_index['date'])

# Add stress indicators
ml_features['stress'] = stress_index.set_index('date')['stress']
ml_features['stress_ma7'] = ml_features['stress'].rolling(7).mean()
ml_features['stress_ma30'] = ml_features['stress'].rolling(30).mean()
ml_features['stress_volatility'] = ml_features['stress'].rolling(30).std()

# Add commodity features
for commodity in commodities:
    prices = commodity_prices.set_index('date')[f'{commodity}_price']
    ml_features[f'{commodity}_return'] = prices.pct_change()
    ml_features[f'{commodity}_volatility'] = prices.pct_change().rolling(30).std()

# Add trade concentration
ml_features['trade_concentration'] = concentration_index.set_index('date')['avg_concentration']

# Add network centrality features
for country in ['USA', 'China', 'Germany']:
    ml_features[f'{country}_centrality'] = centrality_df[centrality_df['country'] == country]['pagerank'].values[0]

# Create crisis labels (stress > 90th percentile in next 30 days)
threshold = ml_features['stress'].quantile(0.9)
ml_features['crisis_next_30d'] = (ml_features['stress'].shift(-30) > threshold).astype(int)

# Remove NaN values
ml_features = ml_features.dropna()

# Prepare data for training
feature_cols = [col for col in ml_features.columns if col != 'crisis_next_30d']
X = ml_features[feature_cols]
y = ml_features['crisis_next_30d']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest model (instead of XGBoost)
print("Training Random Forest classifier...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42
)

rf_model.fit(X_train_scaled, y_train)

# Make predictions
y_pred = rf_model.predict(X_test_scaled)
y_pred_proba = rf_model.predict_proba(X_test_scaled)[:, 1]

# Evaluate model
print("\nCrisis Detection Model Performance:")
print(classification_report(y_test, y_pred))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

# Visualize feature importance
plt.figure(figsize=(10, 6))
top_features = feature_importance.head(10)
plt.barh(top_features['feature'], top_features['importance'])
plt.xlabel('Importance')
plt.title('Top 10 Features for Crisis Detection')
plt.tight_layout()
plt.savefig('/Users/mikaeleage/Research & Analytics Services/Research Workspace/feature_importance.png')
plt.close()
print("✓ Saved feature importance chart")

print(f"\nTop 5 Crisis Indicators:")
for _, row in feature_importance.head(5).iterrows():
    print(f"  {row['feature']}: {row['importance']:.3f}")

# ============================================
# STEP 7: VOLATILITY MODELING
# ============================================
print("\n📊 STEP 7: Financial Volatility Modeling...")

from arch import arch_model

# Model oil price volatility
oil_returns = commodity_prices['Oil_price'].pct_change().dropna() * 100  # Convert to percentage

# Fit GARCH model
print("Fitting GARCH model for oil volatility...")
garch = arch_model(oil_returns, mean='AR', lags=1, vol='GARCH', p=1, q=1)
garch_result = garch.fit(disp='off')

# Forecast volatility
volatility_forecast = garch_result.forecast(horizon=30)
current_volatility = garch_result.conditional_volatility.iloc[-1]
forecast_volatility = np.sqrt(volatility_forecast.variance.values[-1, :])

print(f"\nOil Price Volatility Analysis:")
print(f"  Current volatility: {current_volatility:.2f}%")
print(f"  30-day forecast average: {forecast_volatility.mean():.2f}%")
print(f"  Maximum expected volatility: {forecast_volatility.max():.2f}%")

# Visualize volatility
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Historical volatility
ax1.plot(garch_result.conditional_volatility, alpha=0.7, label='Conditional Volatility')
ax1.set_title('Historical Oil Price Volatility')
ax1.set_ylabel('Volatility (%)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Returns with volatility bands
ax2.plot(oil_returns.index, oil_returns.values, alpha=0.5, label='Returns')
ax2.plot(oil_returns.index, 2 * garch_result.conditional_volatility, 'r--', alpha=0.5, label='±2σ bands')
ax2.plot(oil_returns.index, -2 * garch_result.conditional_volatility, 'r--', alpha=0.5)
ax2.set_title('Oil Returns with Volatility Bands')
ax2.set_ylabel('Returns (%)')
ax2.set_xlabel('Date')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/mikaeleage/Research & Analytics Services/Research Workspace/volatility_analysis.png')
plt.close()
print("✓ Saved volatility analysis")

# ============================================
# STEP 8: INTEGRATED DASHBOARD DATA
# ============================================
print("\n📊 STEP 8: Creating Integrated Dashboard Data...")

# Combine all indicators into one DataFrame
dashboard_data = pd.DataFrame({
    'date': stress_index['date'],
    'supply_stress': stress_index['stress'],
    'stress_forecast': forecast.set_index('ds')['yhat'].reindex(stress_index['date']),
    'crisis_probability': rf_model.predict_proba(scaler.transform(ml_features[feature_cols]))[:, 1],
    'oil_volatility': garch_result.conditional_volatility.reindex(stress_index['date']),
    'trade_concentration': concentration_index.set_index('date')['avg_concentration'].reindex(stress_index['date']),
    'usa_momentum': momentum_index[momentum_index['country'] == 'USA'].set_index('date')['combined_momentum'].reindex(stress_index['date']),
    'china_momentum': momentum_index[momentum_index['country'] == 'China'].set_index('date')['combined_momentum'].reindex(stress_index['date'])
})

# Fill missing values
dashboard_data = dashboard_data.fillna(method='ffill').fillna(0)

# Save dashboard data
dashboard_data.to_csv('/Users/mikaeleage/Research & Analytics Services/Research Workspace/dashboard_data.csv', index=False)
print("✓ Saved integrated dashboard data")

# Create final summary visualization
fig, axes = plt.subplots(4, 1, figsize=(14, 12))

# Panel 1: Supply Chain Stress with Forecast
axes[0].plot(dashboard_data['date'], dashboard_data['supply_stress'], label='Actual', alpha=0.7)
axes[0].plot(dashboard_data['date'], dashboard_data['stress_forecast'], label='Forecast', color='red', alpha=0.7)
axes[0].set_title('Supply Chain Stress Index with Forecast')
axes[0].set_ylabel('Stress Level')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Panel 2: Crisis Probability
axes[1].plot(dashboard_data['date'], dashboard_data['crisis_probability'], color='orange', alpha=0.7)
axes[1].fill_between(dashboard_data['date'], dashboard_data['crisis_probability'], alpha=0.3, color='orange')
axes[1].axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
axes[1].set_title('Crisis Probability (Next 30 Days)')
axes[1].set_ylabel('Probability')
axes[1].set_ylim(0, 1)
axes[1].grid(True, alpha=0.3)

# Panel 3: Economic Momentum Comparison
axes[2].plot(dashboard_data['date'], dashboard_data['usa_momentum'], label='USA', alpha=0.7)
axes[2].plot(dashboard_data['date'], dashboard_data['china_momentum'], label='China', alpha=0.7)
axes[2].set_title('Economic Momentum: USA vs China')
axes[2].set_ylabel('Momentum Index')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

# Panel 4: Market Indicators
ax4_twin = axes[3].twinx()
axes[3].plot(dashboard_data['date'], dashboard_data['oil_volatility'], label='Oil Volatility', color='green', alpha=0.7)
ax4_twin.plot(dashboard_data['date'], dashboard_data['trade_concentration'], label='Trade Concentration', color='purple', alpha=0.7)
axes[3].set_title('Market Risk Indicators')
axes[3].set_ylabel('Oil Volatility (%)', color='green')
ax4_twin.set_ylabel('Trade Concentration (HHI)', color='purple')
axes[3].set_xlabel('Date')
axes[3].grid(True, alpha=0.3)

# Add legends
axes[3].legend(loc='upper left')
ax4_twin.legend(loc='upper right')

plt.tight_layout()
plt.savefig('/Users/mikaeleage/Research & Analytics Services/Research Workspace/integrated_dashboard.png', dpi=300)
plt.close()
print("✓ Saved integrated dashboard visualization")

# ============================================
# FINAL SUMMARY
# ============================================
print("\n" + "="*60)
print("🎉 MACRO ECONOMIC ANALYSIS COMPLETE!")
print("="*60)

print("\n📁 Generated Files:")
print("  1. commodity_prices.png - Historical commodity price trends")
print("  2. trade_network.png - Global trade network visualization")
print("  3. custom_indicators.png - Custom economic indicators")
print("  4. stress_forecast.png - 90-day stress forecast")
print("  5. feature_importance.png - ML model feature importance")
print("  6. volatility_analysis.png - GARCH volatility analysis")
print("  7. integrated_dashboard.png - Complete dashboard view")
print("  8. dashboard_data.csv - All indicators in one file")

print("\n📊 Key Insights:")
print(f"  • Most central country: {centrality_df.sort_values('pagerank', ascending=False).iloc[0]['country']}")
print(f"  • Current stress level: {dashboard_data['supply_stress'].iloc[-1]:.2f}")
print(f"  • Crisis probability: {dashboard_data['crisis_probability'].iloc[-1]:.1%}")
print(f"  • Oil volatility: {dashboard_data['oil_volatility'].iloc[-1]:.1f}%")

print("\n✅ Ready for production dashboard integration!")