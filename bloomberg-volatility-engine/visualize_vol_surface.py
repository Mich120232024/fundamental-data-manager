#!/usr/bin/env python3
"""
FX Volatility Surface Visualization Engine
Creates interactive 3D surfaces and 2D smile plots
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from datetime import datetime
import os
from scipy import interpolate

class VolatilitySurfaceVisualizer:
    """Visualize FX volatility surfaces with multiple plot types"""
    
    def __init__(self, data_file=None):
        # Load latest data file if not specified
        if data_file is None:
            data_dir = "vol_surface_data"
            files = sorted([f for f in os.listdir(data_dir) if f.startswith("vol_surface_")])
            if files:
                data_file = os.path.join(data_dir, files[-1])
        
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        self.timestamp = self.data['timestamp']
        
        # Define tenor mappings to days
        self.tenor_to_days = {
            '1W': 7, '2W': 14, '1M': 30, '2M': 60, '3M': 90,
            '6M': 180, '9M': 270, '1Y': 365
        }
        
        # Define delta mappings for strikes
        self.strike_deltas = {
            '10D Put': 10, '25D Put': 25, 'ATM': 50, 
            '25D Call': 75, '10D Call': 90
        }
    
    def reconstruct_smile(self, pair, tenor):
        """Reconstruct volatility smile for a given pair and tenor"""
        atm_data = self.data['atm_vols'].get(pair, {}).get(tenor, {})
        atm_vol = atm_data.get('vol')
        
        if atm_vol is None:
            return None
        
        smile = {'ATM': atm_vol}
        
        # Get risk reversals and butterflies
        rr_data = self.data['risk_reversals'].get(pair, {})
        bf_data = self.data['butterflies'].get(pair, {})
        
        # 25 Delta
        if '25D' in rr_data and tenor in rr_data['25D'] and '25D' in bf_data and tenor in bf_data['25D']:
            rr_25d = rr_data['25D'][tenor]['rr']
            bf_25d = bf_data['25D'][tenor]['bf']
            
            smile['25D Put'] = atm_vol - 0.5 * rr_25d + bf_25d
            smile['25D Call'] = atm_vol + 0.5 * rr_25d + bf_25d
        
        # 10 Delta
        if '10D' in rr_data and tenor in rr_data['10D'] and '10D' in bf_data and tenor in bf_data['10D']:
            rr_10d = rr_data['10D'][tenor]['rr']
            bf_10d = bf_data['10D'][tenor]['bf']
            
            smile['10D Put'] = atm_vol - 0.5 * rr_10d + bf_10d
            smile['10D Call'] = atm_vol + 0.5 * rr_10d + bf_10d
        
        return smile
    
    def create_surface_matrix(self, pair):
        """Create full volatility surface matrix"""
        tenors = ['1M', '2M', '3M', '6M', '9M', '1Y']
        strikes = ['10D Put', '25D Put', 'ATM', '25D Call', '10D Call']
        
        # Initialize matrix
        surface_matrix = np.full((len(strikes), len(tenors)), np.nan)
        
        for j, tenor in enumerate(tenors):
            smile = self.reconstruct_smile(pair, tenor)
            if smile:
                for i, strike in enumerate(strikes):
                    if strike in smile:
                        surface_matrix[i, j] = smile[strike]
        
        return surface_matrix, strikes, tenors
    
    def interpolate_surface(self, surface_matrix, strikes, tenors, grid_points=50):
        """Interpolate surface for smooth visualization"""
        # Convert to numerical values
        strike_values = [self.strike_deltas[s] for s in strikes]
        tenor_values = [self.tenor_to_days[t] for t in tenors]
        
        # Remove NaN values for interpolation
        valid_points = []
        valid_vols = []
        
        for i, strike in enumerate(strike_values):
            for j, tenor in enumerate(tenor_values):
                if not np.isnan(surface_matrix[i, j]):
                    valid_points.append([strike, tenor])
                    valid_vols.append(surface_matrix[i, j])
        
        if len(valid_points) < 4:
            return None, None, None
        
        # Create fine grid
        strike_grid = np.linspace(10, 90, grid_points)
        tenor_grid = np.linspace(7, 365, grid_points)
        strike_mesh, tenor_mesh = np.meshgrid(strike_grid, tenor_grid)
        
        # Interpolate
        try:
            vol_mesh = interpolate.griddata(
                valid_points, valid_vols, 
                (strike_mesh, tenor_mesh), 
                method='cubic'
            )
        except:
            vol_mesh = interpolate.griddata(
                valid_points, valid_vols, 
                (strike_mesh, tenor_mesh), 
                method='linear'
            )
        
        return strike_mesh, tenor_mesh, vol_mesh
    
    def plot_3d_surface(self, pair, save=True):
        """Create 3D volatility surface plot"""
        surface_matrix, strikes, tenors = self.create_surface_matrix(pair)
        
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # Interpolate for smooth surface
        strike_mesh, tenor_mesh, vol_mesh = self.interpolate_surface(
            surface_matrix, strikes, tenors
        )
        
        if vol_mesh is not None:
            # Plot surface
            surf = ax.plot_surface(
                strike_mesh, tenor_mesh, vol_mesh,
                cmap=cm.viridis, alpha=0.8,
                linewidth=0, antialiased=True
            )
            
            # Add data points
            strike_values = [self.strike_deltas[s] for s in strikes]
            tenor_values = [self.tenor_to_days[t] for t in tenors]
            
            for i, strike in enumerate(strike_values):
                for j, tenor in enumerate(tenor_values):
                    if not np.isnan(surface_matrix[i, j]):
                        ax.scatter(
                            strike, tenor, surface_matrix[i, j],
                            color='red', s=50, alpha=1
                        )
            
            # Labels and formatting
            ax.set_xlabel('Delta (%)', fontsize=12)
            ax.set_ylabel('Days to Expiry', fontsize=12)
            ax.set_zlabel('Implied Volatility (%)', fontsize=12)
            ax.set_title(f'{pair} Volatility Surface\n{self.timestamp}', fontsize=14)
            
            # Add colorbar
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
            
            # Adjust viewing angle
            ax.view_init(elev=20, azim=45)
            
            if save:
                plt.savefig(f'vol_surface_data/{pair}_3d_surface.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        return fig
    
    def plot_smile_curves(self, pair, save=True):
        """Plot volatility smiles for different tenors"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        tenors = ['1M', '3M', '6M', '1Y']
        colors = plt.cm.viridis(np.linspace(0, 1, len(tenors)))
        
        for tenor, color in zip(tenors, colors):
            smile = self.reconstruct_smile(pair, tenor)
            if smile:
                strikes = ['10D Put', '25D Put', 'ATM', '25D Call', '10D Call']
                deltas = [self.strike_deltas[s] for s in strikes]
                vols = [smile.get(s, np.nan) for s in strikes]
                
                # Remove NaN values
                valid_deltas = [d for d, v in zip(deltas, vols) if not np.isnan(v)]
                valid_vols = [v for v in vols if not np.isnan(v)]
                
                if len(valid_deltas) >= 3:
                    # Interpolate for smooth curve
                    delta_smooth = np.linspace(min(valid_deltas), max(valid_deltas), 100)
                    vol_smooth = interpolate.interp1d(
                        valid_deltas, valid_vols, kind='quadratic'
                    )(delta_smooth)
                    
                    ax.plot(delta_smooth, vol_smooth, color=color, 
                           linewidth=2, label=f'{tenor}')
                    ax.scatter(valid_deltas, valid_vols, color=color, s=50)
        
        ax.set_xlabel('Delta (%)', fontsize=12)
        ax.set_ylabel('Implied Volatility (%)', fontsize=12)
        ax.set_title(f'{pair} Volatility Smile\n{self.timestamp}', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save:
            plt.savefig(f'vol_surface_data/{pair}_smile_curves.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        return fig
    
    def plot_term_structure(self, pairs=None, save=True):
        """Plot ATM volatility term structure"""
        if pairs is None:
            pairs = ['EURUSD', 'GBPUSD', 'AUDUSD']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for pair in pairs:
            if pair in self.data['atm_vols']:
                tenors = []
                days = []
                vols = []
                
                for tenor, vol_data in self.data['atm_vols'][pair].items():
                    if vol_data.get('vol'):
                        tenors.append(tenor)
                        days.append(self.tenor_to_days[tenor])
                        vols.append(vol_data['vol'])
                
                if len(days) > 0:
                    # Sort by days
                    sorted_data = sorted(zip(days, vols))
                    days, vols = zip(*sorted_data)
                    
                    ax.plot(days, vols, marker='o', linewidth=2, 
                           markersize=8, label=pair)
        
        ax.set_xlabel('Days to Expiry', fontsize=12)
        ax.set_ylabel('ATM Implied Volatility (%)', fontsize=12)
        ax.set_title(f'FX ATM Volatility Term Structure\n{self.timestamp}', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save:
            plt.savefig('vol_surface_data/term_structure.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        return fig
    
    def plot_heatmap(self, pair, save=True):
        """Create heatmap of volatility surface"""
        surface_matrix, strikes, tenors = self.create_surface_matrix(pair)
        
        # Create DataFrame for better labels
        df = pd.DataFrame(surface_matrix, index=strikes, columns=tenors)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            df, annot=True, fmt='.2f', cmap='RdYlGn_r',
            cbar_kws={'label': 'Implied Volatility (%)'},
            linewidths=0.5
        )
        
        plt.title(f'{pair} Volatility Surface Heatmap\n{self.timestamp}', fontsize=14)
        plt.ylabel('Strike (Delta)', fontsize=12)
        plt.xlabel('Tenor', fontsize=12)
        
        if save:
            plt.savefig(f'vol_surface_data/{pair}_heatmap.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        return plt.gcf()
    
    def create_dashboard(self, pairs=['EURUSD', 'GBPUSD'], save=True):
        """Create comprehensive dashboard with multiple views"""
        fig = plt.figure(figsize=(16, 12))
        
        # Configure grid
        gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], hspace=0.3, wspace=0.3)
        
        for i, pair in enumerate(pairs[:2]):
            # 3D surface
            ax1 = fig.add_subplot(gs[0, i], projection='3d')
            self._add_3d_surface_to_axis(ax1, pair)
            
            # Smile curves
            ax2 = fig.add_subplot(gs[1, i])
            self._add_smile_to_axis(ax2, pair)
            
            # Heatmap
            ax3 = fig.add_subplot(gs[2, i])
            self._add_heatmap_to_axis(ax3, pair)
        
        fig.suptitle(f'FX Volatility Surface Dashboard\n{self.timestamp}', fontsize=16)
        
        if save:
            plt.savefig('vol_surface_data/volatility_dashboard.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        return fig
    
    def _add_3d_surface_to_axis(self, ax, pair):
        """Add 3D surface to existing axis"""
        surface_matrix, strikes, tenors = self.create_surface_matrix(pair)
        strike_mesh, tenor_mesh, vol_mesh = self.interpolate_surface(
            surface_matrix, strikes, tenors, grid_points=30
        )
        
        if vol_mesh is not None:
            surf = ax.plot_surface(
                strike_mesh, tenor_mesh, vol_mesh,
                cmap=cm.viridis, alpha=0.8
            )
            ax.set_xlabel('Delta (%)')
            ax.set_ylabel('Days')
            ax.set_zlabel('Vol (%)')
            ax.set_title(f'{pair} Surface')
            ax.view_init(elev=20, azim=45)
    
    def _add_smile_to_axis(self, ax, pair):
        """Add smile curves to existing axis"""
        tenors = ['1M', '3M', '6M']
        colors = ['blue', 'green', 'red']
        
        for tenor, color in zip(tenors, colors):
            smile = self.reconstruct_smile(pair, tenor)
            if smile:
                strikes = ['10D Put', '25D Put', 'ATM', '25D Call', '10D Call']
                deltas = [self.strike_deltas[s] for s in strikes]
                vols = [smile.get(s, np.nan) for s in strikes]
                
                valid_deltas = [d for d, v in zip(deltas, vols) if not np.isnan(v)]
                valid_vols = [v for v in vols if not np.isnan(v)]
                
                if len(valid_deltas) >= 3:
                    ax.plot(valid_deltas, valid_vols, marker='o', 
                           color=color, label=tenor)
        
        ax.set_xlabel('Delta (%)')
        ax.set_ylabel('Vol (%)')
        ax.set_title(f'{pair} Smile')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _add_heatmap_to_axis(self, ax, pair):
        """Add heatmap to existing axis"""
        surface_matrix, strikes, tenors = self.create_surface_matrix(pair)
        
        im = ax.imshow(surface_matrix, cmap='RdYlGn_r', aspect='auto')
        ax.set_xticks(range(len(tenors)))
        ax.set_xticklabels(tenors)
        ax.set_yticks(range(len(strikes)))
        ax.set_yticklabels(strikes)
        ax.set_title(f'{pair} Heatmap')
        
        # Add values
        for i in range(len(strikes)):
            for j in range(len(tenors)):
                if not np.isnan(surface_matrix[i, j]):
                    ax.text(j, i, f'{surface_matrix[i, j]:.1f}', 
                           ha='center', va='center', fontsize=8)


def main():
    """Generate all visualizations"""
    print("🎨 Generating FX Volatility Surface Visualizations...")
    
    visualizer = VolatilitySurfaceVisualizer()
    
    # Create individual plots for each major pair
    for pair in ['EURUSD', 'GBPUSD', 'AUDUSD']:
        print(f"\nProcessing {pair}...")
        
        # 3D Surface
        print("  - Creating 3D surface...")
        visualizer.plot_3d_surface(pair)
        
        # Smile curves
        print("  - Creating smile curves...")
        visualizer.plot_smile_curves(pair)
        
        # Heatmap
        print("  - Creating heatmap...")
        visualizer.plot_heatmap(pair)
    
    # Term structure comparison
    print("\nCreating term structure comparison...")
    visualizer.plot_term_structure()
    
    # Dashboard
    print("\nCreating comprehensive dashboard...")
    visualizer.create_dashboard()
    
    print("\n✅ All visualizations complete!")
    print("   Files saved in: vol_surface_data/")


if __name__ == "__main__":
    main()