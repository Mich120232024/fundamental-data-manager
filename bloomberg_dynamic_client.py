#!/usr/bin/env python3
"""
Dynamic Bloomberg Client - Convention-Aware API Interface
Zero hardcoding - builds tickers dynamically from Bloomberg conventions
"""
import requests
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

class BloombergClient:
    """Dynamic Bloomberg API client that understands ticker conventions"""
    
    def __init__(self, api_base: str = "http://20.172.249.92:8080", token: str = "test"):
        self.api_base = api_base
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    
    # ==================================
    # BLOOMBERG CONVENTION BUILDERS
    # ==================================
    
    def build_spot_ticker(self, pair: str) -> str:
        """Build spot FX ticker: EURUSD -> EURUSD Curncy"""
        return f"{pair} Curncy"
    
    def build_vol_ticker(self, pair: str, tenor: str) -> str:
        """Build ATM volatility ticker: EURUSD, 1M -> EURUSDV1M Curncy"""
        return f"{pair}V{tenor} Curncy"
    
    def build_rr_ticker(self, pair: str, delta: str, tenor: str) -> str:
        """Build risk reversal ticker: EURUSD, 25, 1M -> EURUSD25RR1M Curncy"""
        return f"{pair}{delta}RR{tenor} Curncy"
    
    def build_bf_ticker(self, pair: str, delta: str, tenor: str) -> str:
        """Build butterfly ticker: EURUSD, 25, 1M -> EURUSD25BF1M Curncy"""
        return f"{pair}{delta}BF{tenor} Curncy"
    
    def build_volatility_surface(self, pair: str, tenors: List[str], deltas: List[str]) -> List[str]:
        """Build complete volatility surface tickers dynamically"""
        securities = []
        
        for tenor in tenors:
            # ATM Vol
            securities.append(self.build_vol_ticker(pair, tenor))
            
            # Risk Reversals and Butterflies for each delta
            for delta in deltas:
                securities.append(self.build_rr_ticker(pair, delta, tenor))
                securities.append(self.build_bf_ticker(pair, delta, tenor))
        
        return securities
    
    # ==================================
    # DYNAMIC API CALLS
    # ==================================
    
    def get_spot_rates(self, pairs: List[str]) -> Dict[str, Any]:
        """Get spot rates for any FX pairs"""
        response = requests.post(
            f"{self.api_base}/api/fx/rates/live",
            json={"currency_pairs": pairs},
            headers=self.headers,
            timeout=10
        )
        return response.json() if response.ok else {"error": response.text}
    
    def get_volatility_surface(self, pairs: List[str], tenors: List[str]) -> Dict[str, Any]:
        """Get volatility surface - dynamically builds all tickers"""
        response = requests.post(
            f"{self.api_base}/api/fx/volatility/live",
            json={"currency_pairs": pairs, "tenors": tenors},
            headers=self.headers,
            timeout=15
        )
        return response.json() if response.ok else {"error": response.text}
    
    def get_custom_securities(self, securities: List[str], fields: List[str] = None) -> Dict[str, Any]:
        """Get any Bloomberg securities you want - fully flexible"""
        if fields is None:
            fields = ["PX_LAST", "PX_BID", "PX_ASK", "LAST_UPDATE_TIME"]
        
        # This would be a generic endpoint that accepts any Bloomberg ticker
        # For now, we work with the existing endpoints
        if all("Curncy" in sec and "V" not in sec for sec in securities):
            # All spot rates
            pairs = [sec.replace(" Curncy", "") for sec in securities]
            return self.get_spot_rates(pairs)
        else:
            # Mixed or volatility data - would need generic endpoint
            return {"error": "Need generic securities endpoint for custom tickers"}
    
    # ==================================
    # CONVENIENCE METHODS
    # ==================================
    
    def get_eurusd_full_surface(self) -> Dict[str, Any]:
        """Get complete EURUSD volatility surface"""
        tenors = ["1W", "2W", "1M", "2M", "3M", "6M", "9M", "1Y", "2Y"]
        return self.get_volatility_surface(["EURUSD"], tenors)
    
    def get_major_pairs_spot(self) -> Dict[str, Any]:
        """Get major FX pairs spot rates"""
        majors = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD"]
        return self.get_spot_rates(majors)
    
    def get_custom_vol_surface(self, pair: str, tenors: List[str], deltas: List[str]) -> List[str]:
        """Build any volatility surface you want"""
        return self.build_volatility_surface(pair, tenors, deltas)
    
    # ==================================
    # BLOOMBERG CONVENTION HELPERS
    # ==================================
    
    @staticmethod
    def parse_vol_ticker(ticker: str) -> Dict[str, str]:
        """Parse volatility ticker back to components"""
        # EURUSDV1M Curncy -> {pair: EURUSD, tenor: 1M}
        # EURUSD25RR1M Curncy -> {pair: EURUSD, delta: 25, type: RR, tenor: 1M}
        
        ticker = ticker.replace(" Curncy", "")
        
        if "V" in ticker and "RR" not in ticker and "BF" not in ticker:
            # ATM Vol: EURUSDV1M
            parts = ticker.split("V")
            return {"pair": parts[0], "tenor": parts[1], "type": "ATM"}
        
        elif "RR" in ticker:
            # Risk Reversal: EURUSD25RR1M
            import re
            match = re.match(r"([A-Z]{6})(\d+)RR(\w+)", ticker)
            if match:
                return {
                    "pair": match.group(1),
                    "delta": match.group(2),
                    "type": "RR",
                    "tenor": match.group(3)
                }
        
        elif "BF" in ticker:
            # Butterfly: EURUSD25BF1M
            import re
            match = re.match(r"([A-Z]{6})(\d+)BF(\w+)", ticker)
            if match:
                return {
                    "pair": match.group(1),
                    "delta": match.group(2),
                    "type": "BF",
                    "tenor": match.group(3)
                }
        
        return {"error": f"Could not parse ticker: {ticker}"}
    
    @staticmethod
    def get_available_deltas() -> List[str]:
        """Get all possible deltas that Bloomberg might support"""
        return ["5", "10", "15", "25", "35", "50"]
    
    @staticmethod
    def get_standard_tenors() -> List[str]:
        """Get standard FX volatility tenors"""
        return ["O/N", "T/N", "1W", "2W", "1M", "2M", "3M", "6M", "9M", "1Y", "2Y"]
    
    @staticmethod
    def get_major_pairs() -> List[str]:
        """Get major FX currency pairs"""
        return ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]

# ==================================
# USAGE EXAMPLES
# ==================================

def demo_dynamic_usage():
    """Show how to use the dynamic client"""
    
    client = BloombergClient()
    
    print("🔴 BLOOMBERG DYNAMIC CLIENT DEMO")
    print("="*50)
    
    # Example 1: Get any spot rates
    print("\n1. Get Major Pairs Spot Rates")
    spots = client.get_major_pairs_spot()
    print(f"Result: {spots.get('data', {}).get('data_count', 0)} rates")
    
    # Example 2: Build custom volatility surface
    print("\n2. Build Custom Volatility Surface")
    custom_surface = client.get_custom_vol_surface("EURUSD", ["1M", "3M"], ["10", "25"])
    print(f"Tickers: {custom_surface[:3]}...")  # Show first 3
    
    # Example 3: Parse any ticker
    print("\n3. Parse Bloomberg Tickers")
    examples = ["EURUSDV1M Curncy", "EURUSD25RR3M Curncy", "GBPUSD10BF6M Curncy"]
    for ticker in examples:
        parsed = client.parse_vol_ticker(ticker)
        print(f"{ticker} -> {parsed}")
    
    # Example 4: Dynamic ticker building
    print("\n4. Dynamic Ticker Building")
    print(f"Spot: {client.build_spot_ticker('GBPJPY')}")
    print(f"Vol: {client.build_vol_ticker('AUDUSD', '6M')}")
    print(f"RR: {client.build_rr_ticker('USDCAD', '25', '1Y')}")
    
    return client

if __name__ == "__main__":
    demo_dynamic_usage()