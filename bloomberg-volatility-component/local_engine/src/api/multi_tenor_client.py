"""
Multi-tenor volatility surface client
"""

import pandas as pd
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from bloomberg_client import BloombergAPIClient
from tenor_mapper import STANDARD_TENORS, get_tenor_order


class MultiTenorVolatilityClient:
    """Client for fetching volatility data across multiple tenors"""
    
    def __init__(self, client: BloombergAPIClient = None):
        self.client = client or BloombergAPIClient()
    
    def get_tenor_surface(self, currency_pair: str, tenor: str) -> Dict[str, Any]:
        """Get volatility surface for a single tenor"""
        try:
            df = self.client.get_fx_volatility_surface(currency_pair, tenor)
            
            # Extract key values
            atm_row = df[df["Product"] == "ATM"].iloc[0] if not df[df["Product"] == "ATM"].empty else None
            rr_25d = df[(df["Product"] == "RR") & (df["Delta"] == "25D")].iloc[0] if not df[(df["Product"] == "RR") & (df["Delta"] == "25D")].empty else None
            bf_25d = df[(df["Product"] == "BF") & (df["Delta"] == "25D")].iloc[0] if not df[(df["Product"] == "BF") & (df["Delta"] == "25D")].empty else None
            rr_10d = df[(df["Product"] == "RR") & (df["Delta"] == "10D")].iloc[0] if not df[(df["Product"] == "RR") & (df["Delta"] == "10D")].empty else None
            bf_10d = df[(df["Product"] == "BF") & (df["Delta"] == "10D")].iloc[0] if not df[(df["Product"] == "BF") & (df["Delta"] == "10D")].empty else None
            
            # Also get other deltas for expanded view
            rr_5d = df[(df["Product"] == "RR") & (df["Delta"] == "5D")].iloc[0] if not df[(df["Product"] == "RR") & (df["Delta"] == "5D")].empty else None
            bf_5d = df[(df["Product"] == "BF") & (df["Delta"] == "5D")].iloc[0] if not df[(df["Product"] == "BF") & (df["Delta"] == "5D")].empty else None
            rr_15d = df[(df["Product"] == "RR") & (df["Delta"] == "15D")].iloc[0] if not df[(df["Product"] == "RR") & (df["Delta"] == "15D")].empty else None
            bf_15d = df[(df["Product"] == "BF") & (df["Delta"] == "15D")].iloc[0] if not df[(df["Product"] == "BF") & (df["Delta"] == "15D")].empty else None
            rr_35d = df[(df["Product"] == "RR") & (df["Delta"] == "35D")].iloc[0] if not df[(df["Product"] == "RR") & (df["Delta"] == "35D")].empty else None
            bf_35d = df[(df["Product"] == "BF") & (df["Delta"] == "35D")].iloc[0] if not df[(df["Product"] == "BF") & (df["Delta"] == "35D")].empty else None
            
            return {
                "tenor": tenor,
                "atm_bid": atm_row["Bid"] if atm_row is not None else None,
                "atm_ask": atm_row["Ask"] if atm_row is not None else None,
                "atm_mid": atm_row["Mid"] if atm_row is not None else None,
                "rr_25d_mid": rr_25d["Mid"] if rr_25d is not None else None,
                "bf_25d_mid": bf_25d["Mid"] if bf_25d is not None else None,
                "rr_10d_mid": rr_10d["Mid"] if rr_10d is not None else None,
                "bf_10d_mid": bf_10d["Mid"] if bf_10d is not None else None,
                # Additional deltas
                "rr_5d_mid": rr_5d["Mid"] if rr_5d is not None else None,
                "bf_5d_mid": bf_5d["Mid"] if bf_5d is not None else None,
                "rr_15d_mid": rr_15d["Mid"] if rr_15d is not None else None,
                "bf_15d_mid": bf_15d["Mid"] if bf_15d is not None else None,
                "rr_35d_mid": rr_35d["Mid"] if rr_35d is not None else None,
                "bf_35d_mid": bf_35d["Mid"] if bf_35d is not None else None,
                "success": True,
                "full_data": df  # Keep full DataFrame for detailed analysis
            }
        except Exception as e:
            return {
                "tenor": tenor,
                "error": str(e),
                "success": False
            }
    
    def get_multi_tenor_surface(self, currency_pair: str = "EURUSD", 
                               tenors: List[str] = None,
                               max_workers: int = 5) -> pd.DataFrame:
        """
        Fetch volatility surface for multiple tenors in parallel
        
        Args:
            currency_pair: Currency pair (default: EURUSD)
            tenors: List of tenors to fetch (default: all standard tenors up to 2Y)
            max_workers: Number of parallel threads
        
        Returns:
            DataFrame with multi-tenor volatility surface
        """
        if tenors is None:
            tenors = STANDARD_TENORS
        
        results = []
        
        # Fetch data in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_tenor = {
                executor.submit(self.get_tenor_surface, currency_pair, tenor): tenor 
                for tenor in tenors
            }
            
            for future in as_completed(future_to_tenor):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    tenor = future_to_tenor[future]
                    results.append({
                        "tenor": tenor,
                        "error": str(e),
                        "success": False
                    })
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Sort by tenor order
        df["tenor_order"] = df["tenor"].apply(get_tenor_order)
        df = df.sort_values("tenor_order").drop("tenor_order", axis=1)
        
        return df
    
    def create_bloomberg_style_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a Bloomberg-style matrix from multi-tenor data"""
        
        # Select columns for Bloomberg-style display
        matrix_df = df[["tenor", "atm_bid", "atm_ask", "atm_mid", 
                       "rr_25d_mid", "bf_25d_mid", "rr_10d_mid", "bf_10d_mid"]].copy()
        
        # Rename columns for display
        matrix_df.columns = ["Exp", "ATM_Bid", "ATM_Ask", "ATM_Mid", 
                            "25D_RR", "25D_BF", "10D_RR", "10D_BF"]
        
        # Replace any NaN/inf values with None for JSON serialization
        import numpy as np
        matrix_df = matrix_df.replace([np.inf, -np.inf], None)
        matrix_df = matrix_df.where(pd.notnull(matrix_df), None)
        
        return matrix_df
    
    def create_full_delta_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a full matrix with all available deltas"""
        
        # Select all columns
        matrix_df = df[["tenor", "atm_bid", "atm_ask", "atm_mid",
                       "rr_5d_mid", "bf_5d_mid", 
                       "rr_10d_mid", "bf_10d_mid",
                       "rr_15d_mid", "bf_15d_mid",
                       "rr_25d_mid", "bf_25d_mid",
                       "rr_35d_mid", "bf_35d_mid"]].copy()
        
        # Rename columns for display
        matrix_df.columns = ["Exp", "ATM_Bid", "ATM_Ask", "ATM_Mid",
                            "5D_RR", "5D_BF", 
                            "10D_RR", "10D_BF",
                            "15D_RR", "15D_BF",
                            "25D_RR", "25D_BF",
                            "35D_RR", "35D_BF"]
        
        # Replace any NaN/inf values with None for JSON serialization
        import numpy as np
        matrix_df = matrix_df.replace([np.inf, -np.inf], None)
        matrix_df = matrix_df.where(pd.notnull(matrix_df), None)
        
        return matrix_df


def main():
    """Example usage"""
    client = MultiTenorVolatilityClient()
    
    print("Fetching multi-tenor volatility surface...")
    
    # Test with a few tenors first
    test_tenors = ["1W", "1M", "3M", "6M", "1Y"]
    df = client.get_multi_tenor_surface("EURUSD", test_tenors)
    
    # Create Bloomberg-style matrix
    matrix = client.create_bloomberg_style_matrix(df)
    
    print("\nBloomberg-Style Volatility Matrix:")
    print(matrix.to_string(index=False, float_format=lambda x: f"{x:.3f}" if pd.notna(x) else "   -   "))
    
    # Show successful vs failed
    successful = df[df["success"] == True].shape[0]
    failed = df[df["success"] == False].shape[0]
    
    print(f"\nSuccess: {successful}, Failed: {failed}")
    
    if failed > 0:
        print("\nFailed tenors:")
        for _, row in df[df["success"] == False].iterrows():
            print(f"  {row['tenor']}: {row.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()