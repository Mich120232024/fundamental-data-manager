#!/usr/bin/env python3
"""
FX Volatility Surface Data Collection System
Collects and stores all necessary data to reconstruct historical volatility surfaces
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, List, Tuple
import numpy as np

class FXVolatilitySurfaceCollector:
    """Collects FX volatility surface data from Bloomberg Terminal"""
    
    def __init__(self, base_url: str = "http://20.172.249.92:8080"):
        self.base_url = base_url
        self.data_dir = "vol_surface_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Define currency pairs to collect
        self.fx_pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF"]
        
        # Define tenors
        self.tenors = ["1W", "2W", "1M", "2M", "3M", "6M", "9M", "1Y"]
        
        # Define smile points (delta)
        self.deltas = ["10", "25"]
    
    def collect_spot_rates(self) -> Dict[str, float]:
        """Collect current spot rates for all FX pairs"""
        spot_rates = {}
        
        for pair in self.fx_pairs:
            ticker = f"{pair} Curncy"
            response = requests.post(
                f"{self.base_url}/api/market-data",
                json={"securities": [ticker], "fields": ["PX_LAST", "PX_BID", "PX_ASK"]}
            )
            
            if response.status_code == 200:
                data = response.json()[0]["fields"]
                spot_rates[pair] = {
                    "spot": data.get("PX_LAST"),
                    "bid": data.get("PX_BID"),
                    "ask": data.get("PX_ASK"),
                    "mid": (data.get("PX_BID", 0) + data.get("PX_ASK", 0)) / 2 if data.get("PX_BID") else data.get("PX_LAST")
                }
        
        return spot_rates
    
    def collect_atm_vols(self) -> Dict[str, Dict[str, float]]:
        """Collect ATM implied volatilities for all tenors"""
        atm_vols = {}
        
        for pair in self.fx_pairs:
            atm_vols[pair] = {}
            
            for tenor in self.tenors:
                ticker = f"{pair}V{tenor} Curncy"
                response = requests.post(
                    f"{self.base_url}/api/market-data",
                    json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID", "PX_BID", "PX_ASK"]}
                )
                
                if response.status_code == 200:
                    data = response.json()[0]["fields"]
                    atm_vols[pair][tenor] = {
                        "vol": data.get("PX_LAST"),
                        "bid": data.get("PX_BID"),
                        "ask": data.get("PX_ASK"),
                        "mid": data.get("PX_MID", data.get("PX_LAST"))
                    }
        
        return atm_vols
    
    def collect_risk_reversals(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Collect risk reversals for different deltas and tenors"""
        risk_reversals = {}
        
        for pair in self.fx_pairs:
            risk_reversals[pair] = {}
            pair_code = pair[:3]  # EUR, GBP, USD, etc.
            
            for delta in self.deltas:
                risk_reversals[pair][f"{delta}D"] = {}
                
                for tenor in ["1M", "3M", "6M", "1Y"]:  # RR typically quoted for these tenors
                    ticker = f"{pair_code}{delta}R{tenor} Curncy"
                    response = requests.post(
                        f"{self.base_url}/api/market-data",
                        json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID", "PX_BID", "PX_ASK"]}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()[0]["fields"]
                        if data.get("PX_LAST") is not None:
                            risk_reversals[pair][f"{delta}D"][tenor] = {
                                "rr": data.get("PX_LAST"),
                                "bid": data.get("PX_BID"),
                                "ask": data.get("PX_ASK"),
                                "mid": data.get("PX_MID", data.get("PX_LAST"))
                            }
        
        return risk_reversals
    
    def collect_butterflies(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Collect butterfly spreads for different deltas and tenors"""
        butterflies = {}
        
        for pair in self.fx_pairs:
            butterflies[pair] = {}
            pair_code = pair[:3]
            
            for delta in self.deltas:
                butterflies[pair][f"{delta}D"] = {}
                
                for tenor in ["1M", "3M", "6M", "1Y"]:
                    ticker = f"{pair_code}{delta}B{tenor} Curncy"
                    response = requests.post(
                        f"{self.base_url}/api/market-data",
                        json={"securities": [ticker], "fields": ["PX_LAST", "PX_MID", "PX_BID", "PX_ASK"]}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()[0]["fields"]
                        if data.get("PX_LAST") is not None:
                            butterflies[pair][f"{delta}D"][tenor] = {
                                "bf": data.get("PX_LAST"),
                                "bid": data.get("PX_BID"),
                                "ask": data.get("PX_ASK"),
                                "mid": data.get("PX_MID", data.get("PX_LAST"))
                            }
        
        return butterflies
    
    def collect_full_surface(self) -> Dict:
        """Collect all data needed for volatility surface reconstruction"""
        timestamp = datetime.now()
        
        print(f"🔄 Collecting volatility surface data at {timestamp}")
        
        # Collect all components
        surface_data = {
            "timestamp": timestamp.isoformat(),
            "spot_rates": self.collect_spot_rates(),
            "atm_vols": self.collect_atm_vols(),
            "risk_reversals": self.collect_risk_reversals(),
            "butterflies": self.collect_butterflies()
        }
        
        # Save to file
        filename = f"{self.data_dir}/vol_surface_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(surface_data, f, indent=2)
        
        print(f"✅ Saved volatility surface data to {filename}")
        
        return surface_data
    
    def reconstruct_smile(self, atm_vol: float, rr_25d: float, bf_25d: float, 
                         rr_10d: float = None, bf_10d: float = None) -> Dict[str, float]:
        """
        Reconstruct volatility smile from ATM, risk reversals, and butterflies
        
        Formula:
        σ_25D_Call = ATM + 0.5 * RR_25D + BF_25D
        σ_25D_Put = ATM - 0.5 * RR_25D + BF_25D
        """
        smile = {
            "atm": atm_vol,
            "25d_call": atm_vol + 0.5 * rr_25d + bf_25d,
            "25d_put": atm_vol - 0.5 * rr_25d + bf_25d
        }
        
        if rr_10d is not None and bf_10d is not None:
            smile["10d_call"] = atm_vol + 0.5 * rr_10d + bf_10d
            smile["10d_put"] = atm_vol - 0.5 * rr_10d + bf_10d
        
        return smile
    
    def generate_surface_report(self, surface_data: Dict) -> str:
        """Generate a summary report of collected surface data"""
        report = []
        report.append("FX VOLATILITY SURFACE REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {surface_data['timestamp']}")
        report.append("")
        
        for pair in self.fx_pairs:
            if pair in surface_data['spot_rates']:
                report.append(f"\n{pair}")
                report.append("-" * 20)
                
                # Spot rate
                spot = surface_data['spot_rates'][pair]
                if spot['spot']:
                    report.append(f"Spot: {spot['spot']:.4f}")
                
                # ATM vols
                if pair in surface_data['atm_vols']:
                    report.append("\nATM Volatilities:")
                    for tenor, vol_data in surface_data['atm_vols'][pair].items():
                        if vol_data['vol']:
                            report.append(f"  {tenor}: {vol_data['vol']:.2f}%")
                
                # Risk Reversals
                if pair in surface_data['risk_reversals']:
                    report.append("\nRisk Reversals:")
                    for delta, tenors in surface_data['risk_reversals'][pair].items():
                        for tenor, rr_data in tenors.items():
                            if rr_data['rr'] is not None:
                                report.append(f"  {delta} {tenor}: {rr_data['rr']:.3f}%")
                
                # Butterflies
                if pair in surface_data['butterflies']:
                    report.append("\nButterflies:")
                    for delta, tenors in surface_data['butterflies'][pair].items():
                        for tenor, bf_data in tenors.items():
                            if bf_data['bf'] is not None:
                                report.append(f"  {delta} {tenor}: {bf_data['bf']:.3f}%")
        
        return "\n".join(report)
    
    def create_surface_dataframe(self, surface_data: Dict) -> pd.DataFrame:
        """Convert surface data to pandas DataFrame for analysis"""
        rows = []
        
        for pair in self.fx_pairs:
            # Add spot rate
            if pair in surface_data['spot_rates']:
                spot = surface_data['spot_rates'][pair]['spot']
            else:
                spot = None
            
            # Add ATM vols
            if pair in surface_data['atm_vols']:
                for tenor, vol_data in surface_data['atm_vols'][pair].items():
                    if vol_data['vol']:
                        row = {
                            'timestamp': surface_data['timestamp'],
                            'pair': pair,
                            'spot': spot,
                            'tenor': tenor,
                            'strike_type': 'ATM',
                            'delta': 50,
                            'volatility': vol_data['vol'],
                            'bid_vol': vol_data.get('bid'),
                            'ask_vol': vol_data.get('ask')
                        }
                        rows.append(row)
        
        return pd.DataFrame(rows)


def main():
    """Main collection routine"""
    collector = FXVolatilitySurfaceCollector()
    
    # Collect full surface
    surface_data = collector.collect_full_surface()
    
    # Generate report
    report = collector.generate_surface_report(surface_data)
    print("\n" + report)
    
    # Save report
    with open(f"{collector.data_dir}/latest_report.txt", 'w') as f:
        f.write(report)
    
    # Create DataFrame
    df = collector.create_surface_dataframe(surface_data)
    df.to_csv(f"{collector.data_dir}/latest_surface.csv", index=False)
    
    print(f"\n✅ Collection complete. Files saved in {collector.data_dir}/")


if __name__ == "__main__":
    main()