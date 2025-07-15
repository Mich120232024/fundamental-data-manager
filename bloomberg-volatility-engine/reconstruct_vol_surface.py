#!/usr/bin/env python3
"""
Reconstruct and visualize FX volatility surface from collected data
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
import os

class VolatilitySurfaceReconstructor:
    """Reconstruct volatility surface from market quotes"""
    
    def __init__(self, data_file=None):
        # Load latest data file if not specified
        if data_file is None:
            data_dir = "vol_surface_data"
            files = sorted([f for f in os.listdir(data_dir) if f.startswith("vol_surface_")])
            if files:
                data_file = os.path.join(data_dir, files[-1])
            else:
                raise ValueError("No data files found")
        
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        print(f"Loaded data from: {data_file}")
        print(f"Timestamp: {self.data['timestamp']}")
    
    def reconstruct_smile(self, pair: str, tenor: str):
        """
        Reconstruct volatility smile for a specific pair and tenor
        
        Uses the market standard formulas:
        - σ(25D Call) = σ(ATM) + 0.5 × RR(25D) + BF(25D)
        - σ(25D Put)  = σ(ATM) - 0.5 × RR(25D) + BF(25D)
        - σ(10D Call) = σ(ATM) + 0.5 × RR(10D) + BF(10D)
        - σ(10D Put)  = σ(ATM) - 0.5 × RR(10D) + BF(10D)
        """
        # Get ATM vol
        atm_data = self.data['atm_vols'].get(pair, {}).get(tenor, {})
        atm_vol = atm_data.get('vol')
        
        if atm_vol is None:
            return None
        
        smile = {
            'strikes': ['10D Put', '25D Put', 'ATM', '25D Call', '10D Call'],
            'vols': [None, None, atm_vol, None, None],
            'deltas': [10, 25, 50, 75, 90]  # Approximate delta values
        }
        
        # Get risk reversals and butterflies
        rr_data = self.data['risk_reversals'].get(pair, {})
        bf_data = self.data['butterflies'].get(pair, {})
        
        # 25 Delta
        if '25D' in rr_data and tenor in rr_data['25D'] and '25D' in bf_data and tenor in bf_data['25D']:
            rr_25d = rr_data['25D'][tenor]['rr']
            bf_25d = bf_data['25D'][tenor]['bf']
            
            smile['vols'][1] = atm_vol - 0.5 * rr_25d + bf_25d  # 25D Put
            smile['vols'][3] = atm_vol + 0.5 * rr_25d + bf_25d  # 25D Call
        
        # 10 Delta
        if '10D' in rr_data and tenor in rr_data['10D'] and '10D' in bf_data and tenor in bf_data['10D']:
            rr_10d = rr_data['10D'][tenor]['rr']
            bf_10d = bf_data['10D'][tenor]['bf']
            
            smile['vols'][0] = atm_vol - 0.5 * rr_10d + bf_10d  # 10D Put
            smile['vols'][4] = atm_vol + 0.5 * rr_10d + bf_10d  # 10D Call
        
        return smile
    
    def create_surface_matrix(self, pair: str):
        """Create a volatility surface matrix for a currency pair"""
        tenors = ['1M', '3M', '6M', '1Y']
        strikes = ['10D Put', '25D Put', 'ATM', '25D Call', '10D Call']
        
        # Initialize matrix
        surface = pd.DataFrame(index=strikes, columns=tenors)
        
        for tenor in tenors:
            smile = self.reconstruct_smile(pair, tenor)
            if smile:
                for i, strike in enumerate(strikes):
                    if smile['vols'][i] is not None:
                        surface.loc[strike, tenor] = smile['vols'][i]
        
        return surface
    
    def generate_report(self):
        """Generate a comprehensive volatility surface report"""
        report = []
        report.append("=" * 80)
        report.append("FX VOLATILITY SURFACE RECONSTRUCTION")
        report.append(f"As of: {self.data['timestamp']}")
        report.append("=" * 80)
        
        for pair in ['EURUSD', 'GBPUSD', 'AUDUSD']:
            report.append(f"\n\n{pair} VOLATILITY SURFACE")
            report.append("-" * 40)
            
            # Spot rate
            spot_data = self.data['spot_rates'].get(pair, {})
            if spot_data.get('spot'):
                report.append(f"Spot: {spot_data['spot']:.4f}")
            
            # Create surface matrix
            surface = self.create_surface_matrix(pair)
            
            if not surface.empty:
                report.append("\nImplied Volatility Surface (%):")
                report.append(surface.to_string(float_format=lambda x: f"{x:.2f}" if pd.notna(x) else ""))
                
                # Show smile for 1M tenor as example
                smile_1m = self.reconstruct_smile(pair, '1M')
                if smile_1m and all(v is not None for v in smile_1m['vols']):
                    report.append("\n1-Month Volatility Smile:")
                    for strike, vol in zip(smile_1m['strikes'], smile_1m['vols']):
                        if vol is not None:
                            report.append(f"  {strike:>10}: {vol:6.2f}%")
                    
                    # Calculate smile metrics
                    atm = smile_1m['vols'][2]
                    put_25d = smile_1m['vols'][1]
                    call_25d = smile_1m['vols'][3]
                    
                    report.append("\nSmile Characteristics:")
                    report.append(f"  Risk Reversal (25D): {call_25d - put_25d:6.3f}%")
                    report.append(f"  Butterfly (25D):     {(call_25d + put_25d)/2 - atm:6.3f}%")
                    report.append(f"  Skew Direction:      {'Call Premium' if call_25d > put_25d else 'Put Premium'}")
        
        # Add surface interpolation notes
        report.append("\n\n" + "=" * 80)
        report.append("SURFACE INTERPOLATION NOTES")
        report.append("=" * 80)
        report.append("\n1. Smile Construction:")
        report.append("   - σ(K) = σ(ATM) + RR × δ(K) + BF × δ(K)²")
        report.append("   - Where δ(K) maps strike K to delta space")
        
        report.append("\n2. Tenor Interpolation:")
        report.append("   - Use variance interpolation: σ²(t) × t")
        report.append("   - Smooth across term structure")
        
        report.append("\n3. Missing Data:")
        report.append("   - Some pairs lack complete RR/BF quotes")
        report.append("   - Use SABR or SVI model for full surface")
        
        return "\n".join(report)
    
    def export_for_analysis(self, output_file="vol_surface_analysis.csv"):
        """Export surface data in format suitable for further analysis"""
        rows = []
        
        for pair in self.data['spot_rates'].keys():
            spot = self.data['spot_rates'][pair]['spot']
            
            # ATM vols
            for tenor, vol_data in self.data['atm_vols'].get(pair, {}).items():
                if vol_data.get('vol'):
                    rows.append({
                        'timestamp': self.data['timestamp'],
                        'pair': pair,
                        'spot': spot,
                        'tenor': tenor,
                        'strike_type': 'ATM',
                        'delta': 50,
                        'volatility': vol_data['vol'],
                        'bid': vol_data.get('bid'),
                        'ask': vol_data.get('ask')
                    })
            
            # Reconstruct smile points
            for tenor in ['1M', '3M', '6M', '1Y']:
                smile = self.reconstruct_smile(pair, tenor)
                if smile:
                    strike_map = {
                        '10D Put': (10, 'Put'),
                        '25D Put': (25, 'Put'), 
                        'ATM': (50, 'ATM'),
                        '25D Call': (75, 'Call'),
                        '10D Call': (90, 'Call')
                    }
                    
                    for i, (strike, vol) in enumerate(zip(smile['strikes'], smile['vols'])):
                        if vol is not None and strike != 'ATM':  # Skip ATM as already added
                            delta, option_type = strike_map[strike]
                            rows.append({
                                'timestamp': self.data['timestamp'],
                                'pair': pair,
                                'spot': spot,
                                'tenor': tenor,
                                'strike_type': strike,
                                'delta': delta,
                                'volatility': vol,
                                'bid': None,
                                'ask': None
                            })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False)
        print(f"\nExported analysis data to: {output_file}")
        
        return df


def main():
    """Main execution"""
    reconstructor = VolatilitySurfaceReconstructor()
    
    # Generate report
    report = reconstructor.generate_report()
    print(report)
    
    # Save report
    with open("vol_surface_data/surface_reconstruction_report.txt", 'w') as f:
        f.write(report)
    
    # Export for analysis
    df = reconstructor.export_for_analysis()
    
    print("\n✅ Volatility surface reconstruction complete!")
    print(f"   - Report saved to: vol_surface_data/surface_reconstruction_report.txt")
    print(f"   - Analysis data saved to: vol_surface_analysis.csv")
    print(f"   - Total data points: {len(df)}")


if __name__ == "__main__":
    main()