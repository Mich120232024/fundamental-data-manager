#!/usr/bin/env python3
"""Test the volatility surface shape after Vanna-Volga fix"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Simulate the Vanna-Volga calculation
def vanna_volga_vol(strike, spot, atm_vol, rr, bf, maturity):
    """Calculate volatility using Vanna-Volga formula"""
    forward = spot
    sigma = atm_vol / 100
    T = maturity
    
    # Calculate 25D strikes
    d25 = 0.674  # N^-1(0.25)
    k_25P = forward * np.exp(-d25 * sigma * np.sqrt(T) + 0.5 * sigma**2 * T)
    k_25C = forward * np.exp(d25 * sigma * np.sqrt(T) + 0.5 * sigma**2 * T)
    
    # Market volatilities
    vol_25P = atm_vol + bf - rr/2
    vol_25C = atm_vol + bf + rr/2
    vol_ATM = atm_vol
    
    # Log-moneyness
    x = np.log(strike / forward)
    x_25P = np.log(k_25P / forward)
    x_ATM = 0
    x_25C = np.log(k_25C / forward)
    
    # Vanna-Volga weights
    w1 = (x - x_ATM) * (x - x_25C) / ((x_25P - x_ATM) * (x_25P - x_25C))
    w2 = (x - x_25P) * (x - x_25C) / ((x_ATM - x_25P) * (x_ATM - x_25C))
    w3 = (x - x_25P) * (x - x_ATM) / ((x_25C - x_25P) * (x_25C - x_ATM))
    
    # Calculate volatility
    vol = w1 * vol_25P + w2 * vol_ATM + w3 * vol_25C
    
    # Wing extrapolation
    if strike < k_25P * 0.9:
        extrapolation = (k_25P - strike) / k_25P
        vol += extrapolation * 2.0 * abs(vol_25P - vol_ATM)
    elif strike > k_25C * 1.1:
        extrapolation = (strike - k_25C) / k_25C
        vol += extrapolation * 2.0 * abs(vol_25C - vol_ATM)
    
    return max(4.0, min(20.0, vol))

# Test parameters
spot = 1.0833
tenors = [1/12, 3/12, 6/12, 1]  # 1M, 3M, 6M, 1Y
tenor_labels = ['1M', '3M', '6M', '1Y']

# Market data (from Bloomberg)
market_data = {
    '1M': {'atm': 7.64, 'rr': -0.045, 'bf': 0.158},
    '3M': {'atm': 7.58, 'rr': 0.170, 'bf': 0.187},
    '6M': {'atm': 7.54, 'rr': 0.340, 'bf': 0.218},
    '1Y': {'atm': 7.50, 'rr': 0.425, 'bf': 0.237}
}

# Generate surface
strikes = np.linspace(0.95, 1.22, 50)
fig = plt.figure(figsize=(12, 8))

# 2D smile plot
ax1 = fig.add_subplot(121)
for i, (tenor, label) in enumerate(zip(tenors, tenor_labels)):
    data = market_data[label]
    vols = [vanna_volga_vol(k, spot, data['atm'], data['rr'], data['bf'], tenor) for k in strikes]
    ax1.plot(strikes, vols, label=label, linewidth=2)

ax1.set_xlabel('Strike')
ax1.set_ylabel('Implied Volatility (%)')
ax1.set_title('Vanna-Volga Volatility Smile')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 3D surface plot
ax2 = fig.add_subplot(122, projection='3d')
X, Y = np.meshgrid(strikes, range(len(tenors)))
Z = np.zeros_like(X)

for j, (tenor, label) in enumerate(zip(tenors, tenor_labels)):
    data = market_data[label]
    for i, strike in enumerate(strikes):
        Z[j, i] = vanna_volga_vol(strike, spot, data['atm'], data['rr'], data['bf'], tenor)

surf = ax2.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
ax2.set_xlabel('Strike')
ax2.set_ylabel('Tenor')
ax2.set_zlabel('Implied Vol (%)')
ax2.set_title('Volatility Surface (Vanna-Volga)')
ax2.set_yticks(range(len(tenors)))
ax2.set_yticklabels(tenor_labels)

plt.tight_layout()
plt.savefig('vanna_volga_surface_test.png', dpi=150)
print("Surface plot saved as vanna_volga_surface_test.png")

# Print smile characteristics
print("\n=== Smile Characteristics ===")
for label in tenor_labels:
    data = market_data[label]
    tenor = tenors[tenor_labels.index(label)]
    
    # Calculate key points
    atm_vol = data['atm']
    vol_10p = vanna_volga_vol(1.00, spot, data['atm'], data['rr'], data['bf'], tenor)
    vol_25p = vanna_volga_vol(1.04, spot, data['atm'], data['rr'], data['bf'], tenor)
    vol_atm = vanna_volga_vol(spot, spot, data['atm'], data['rr'], data['bf'], tenor)
    vol_25c = vanna_volga_vol(1.13, spot, data['atm'], data['rr'], data['bf'], tenor)
    vol_10c = vanna_volga_vol(1.17, spot, data['atm'], data['rr'], data['bf'], tenor)
    
    print(f"\n{label}:")
    print(f"  10D Put: {vol_10p:.2f}%")
    print(f"  25D Put: {vol_25p:.2f}%")
    print(f"  ATM: {vol_atm:.2f}%")
    print(f"  25D Call: {vol_25c:.2f}%")
    print(f"  10D Call: {vol_10c:.2f}%")
    print(f"  Smile range: {min(vol_10p, vol_10c):.2f}% - {max(vol_10p, vol_10c):.2f}%")