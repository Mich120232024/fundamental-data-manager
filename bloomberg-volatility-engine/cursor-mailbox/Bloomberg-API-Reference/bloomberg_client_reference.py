#!/usr/bin/env python3
"""
Bloomberg API Client Reference
This is the correct client to use with the real_bloomberg_api.py server
Server URL: http://20.172.249.92:8080
"""

import requests
import json
from typing import List, Dict, Optional

class BloombergClient:
    """Client for accessing Bloomberg Terminal API Server"""
    
    def __init__(self, server_url: str = "http://20.172.249.92:8080"):
        """Initialize Bloomberg client with the correct server URL"""
        self.server_url = server_url
        self.session = requests.Session()
    
    def check_health(self) -> Dict:
        """Check if Bloomberg Terminal is connected"""
        response = self.session.get(f"{self.server_url}/health")
        return response.json()
    
    def get_market_data(self, securities: List[str], fields: List[str]) -> Dict:
        """
        Get market data from Bloomberg Terminal
        
        Args:
            securities: List of Bloomberg security IDs (e.g., ["EURUSD Curncy", "AAPL US Equity"])
            fields: List of fields to retrieve (e.g., ["PX_LAST", "VOLUME"])
        
        Returns:
            Dict with security data
        """
        payload = {
            "securities": securities,
            "fields": fields
        }
        response = self.session.post(
            f"{self.server_url}/api/market-data",
            json=payload
        )
        return response.json()
    
    def get_fx_rates(self) -> Dict:
        """Get FX rates for major currency pairs"""
        response = self.session.get(f"{self.server_url}/api/fx/rates")
        return response.json()

# Example usage for volatility surface data
if __name__ == "__main__":
    client = BloombergClient()
    
    # Check health
    health = client.check_health()
    print(f"Bloomberg Terminal Connected: {health.get('bloomberg_connected')}")
    
    # Get FX volatility data
    vol_securities = [
        "EURUSDV1M Curncy",  # 1-month ATM vol
        "EURUSDV2M Curncy",  # 2-month ATM vol
        "EURUSDV3M Curncy",  # 3-month ATM vol
        "EUR25R1M Curncy",   # 1-month 25-delta risk reversal
        "EUR25B1M Curncy",   # 1-month 25-delta butterfly
    ]
    
    vol_data = client.get_market_data(vol_securities, ["PX_LAST"])
    print(json.dumps(vol_data, indent=2))