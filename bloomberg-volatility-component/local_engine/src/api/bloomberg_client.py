"""
Bloomberg API Client for Local Analysis
This connects to the Bloomberg API running on VM (20.172.249.92:8080)
"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd


class BloombergAPIClient:
    """Client for Bloomberg API running on Azure VM"""
    
    def __init__(self, base_url: str = "http://20.172.249.92:8080", api_key: str = "test"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Bloomberg API is healthy"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def get_reference_data(self, securities: List[str], fields: List[str]) -> Dict[str, Any]:
        """Get reference data for securities"""
        payload = {
            "securities": securities,
            "fields": fields
        }
        response = requests.post(
            f"{self.base_url}/api/bloomberg/reference",
            json=payload,
            headers=self.headers
        )
        return response.json()
    
    def get_fx_volatility_surface(self, currency_pair: str = "EURUSD", tenor: str = "1M") -> pd.DataFrame:
        """
        Get complete volatility surface for a currency pair and tenor
        Returns a DataFrame with strikes, products, and values
        """
        # Build all securities for the volatility surface
        securities = []
        
        # ATM
        securities.append(f"{currency_pair}V{tenor} BGN Curncy")
        
        # Risk Reversals and Butterflies for all available deltas
        # Note: Bloomberg only supports 5, 10, 15, 25, 35 deltas (not 20, 30, 40, 45)
        for delta in ["5", "10", "15", "25", "35"]:
            securities.append(f"{currency_pair}{delta}R{tenor} BGN Curncy")  # Risk Reversal
            securities.append(f"{currency_pair}{delta}B{tenor} BGN Curncy")  # Butterfly
        
        # Fields to retrieve
        fields = ["PX_LAST", "PX_BID", "PX_ASK"]
        
        # Get data from Bloomberg
        response = self.get_reference_data(securities, fields)
        
        if response.get("success"):
            # Process response into DataFrame
            data_rows = []
            
            for sec_data in response["data"]["securities_data"]:
                if sec_data["success"]:
                    security = sec_data["security"]
                    fields_data = sec_data["fields"]
                    
                    # Parse security to get product type and delta
                    sec_parts = security.replace(" BGN Curncy", "").replace(currency_pair, "")
                    
                    if "V" in sec_parts and "R" not in sec_parts and "B" not in sec_parts:
                        product = "ATM"
                        delta = "ATM"
                    elif "R" in sec_parts and "B" not in sec_parts:
                        product = "RR"
                        # Extract delta (e.g., "25" from "25R1M")
                        delta = sec_parts.split("R")[0] + "D"
                    elif "B" in sec_parts and "R" not in sec_parts:
                        product = "BF"
                        # Extract delta
                        delta = sec_parts.split("B")[0] + "D"
                    else:
                        continue
                    
                    data_rows.append({
                        "Currency_Pair": currency_pair,
                        "Tenor": tenor,
                        "Delta": delta,
                        "Product": product,
                        "Mid": fields_data.get("PX_LAST"),
                        "Bid": fields_data.get("PX_BID"),
                        "Ask": fields_data.get("PX_ASK"),
                        "Spread": fields_data.get("PX_ASK", 0) - fields_data.get("PX_BID", 0) if fields_data.get("PX_ASK") and fields_data.get("PX_BID") else None
                    })
            
            # Create DataFrame
            df = pd.DataFrame(data_rows)
            
            # Sort by product type and delta
            sort_order = {"ATM": 0, "RR": 1, "BF": 2}
            delta_order = {"ATM": 0, "5D": 1, "10D": 2, "15D": 3, "25D": 4, "35D": 5}
            
            df["product_sort"] = df["Product"].map(sort_order)
            df["delta_sort"] = df["Delta"].map(delta_order)
            df = df.sort_values(["product_sort", "delta_sort"]).drop(columns=["product_sort", "delta_sort"])
            
            return df
        else:
            raise Exception(f"API Error: {response.get('error', 'Unknown error')}")
    
    def get_historical_data(self, security: str, fields: List[str], 
                          start_date: str, end_date: str, 
                          periodicity: str = "DAILY") -> pd.DataFrame:
        """Get historical data for a security"""
        payload = {
            "security": security,
            "fields": fields,
            "start_date": start_date,
            "end_date": end_date,
            "periodicity": periodicity
        }
        response = requests.post(
            f"{self.base_url}/api/bloomberg/historical",
            json=payload,
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data", {}).get("data"):
                # Convert to DataFrame
                df = pd.DataFrame(data["data"]["data"])
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
                return df
            else:
                raise Exception(f"API Error: {data.get('error', 'No data returned')}")
        else:
            raise Exception(f"HTTP Error {response.status_code}: {response.text}")


if __name__ == "__main__":
    # Example usage
    client = BloombergAPIClient()
    
    # Check health
    print("Health Check:")
    print(client.health_check())
    
    # Get EURUSD volatility surface
    print("\nEURUSD 1M Volatility Surface:")
    vol_surface = client.get_fx_volatility_surface("EURUSD", "1M")
    print(vol_surface)