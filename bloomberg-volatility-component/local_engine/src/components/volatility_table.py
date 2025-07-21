"""
Bloomberg-style Volatility Surface Table Display
Renders FX volatility surface data in a format similar to Bloomberg Terminal
"""

import pandas as pd
from typing import Optional
from datetime import datetime
from tabulate import tabulate
import sys
sys.path.append('..')
from api.bloomberg_client import BloombergAPIClient


class VolatilitySurfaceTable:
    """Display volatility surface in Bloomberg-style format"""
    
    def __init__(self, client: BloombergAPIClient):
        self.client = client
    
    def format_value(self, value: Optional[float], decimals: int = 3) -> str:
        """Format numeric value with proper decimals and handling None"""
        if value is None:
            return "   -   "
        return f"{value:7.{decimals}f}"
    
    def format_spread(self, bid: Optional[float], ask: Optional[float]) -> str:
        """Format bid/ask spread"""
        if bid is None or ask is None:
            return "   -   "
        spread = ask - bid
        return f"{spread:7.3f}"
    
    def create_bloomberg_style_table(self, currency_pair: str = "EURUSD", tenor: str = "1M") -> str:
        """Create a Bloomberg Terminal style volatility surface table"""
        
        # Get volatility surface data
        df = self.client.get_fx_volatility_surface(currency_pair, tenor)
        
        # Create header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    BLOOMBERG FX VOLATILITY SURFACE                           ║
║                    {currency_pair} {tenor} - {timestamp}                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        # Prepare data for table
        table_data = []
        
        # ATM row
        atm_row = df[df["Product"] == "ATM"].iloc[0]
        table_data.append([
            "ATM",
            "",
            self.format_value(atm_row["Bid"]),
            self.format_value(atm_row["Mid"]),
            self.format_value(atm_row["Ask"]),
            self.format_spread(atm_row["Bid"], atm_row["Ask"])
        ])
        
        # Add separator
        table_data.append(["", "", "", "", "", ""])
        
        # Risk Reversals
        table_data.append(["RISK REVERSALS", "", "", "", "", ""])
        for _, row in df[df["Product"] == "RR"].iterrows():
            table_data.append([
                f"  {row['Delta']}",
                "",
                self.format_value(row["Bid"]),
                self.format_value(row["Mid"]),
                self.format_value(row["Ask"]),
                self.format_spread(row["Bid"], row["Ask"])
            ])
        
        # Add separator
        table_data.append(["", "", "", "", "", ""])
        
        # Butterflies
        table_data.append(["BUTTERFLIES", "", "", "", "", ""])
        for _, row in df[df["Product"] == "BF"].iterrows():
            table_data.append([
                f"  {row['Delta']}",
                "",
                self.format_value(row["Bid"]),
                self.format_value(row["Mid"]),
                self.format_value(row["Ask"]),
                self.format_spread(row["Bid"], row["Ask"])
            ])
        
        # Create table
        headers = ["Strike", "", "Bid", "Mid", "Ask", "Spread"]
        table = tabulate(table_data, headers=headers, tablefmt="simple", 
                        colalign=("left", "center", "right", "right", "right", "right"))
        
        # Add box drawing characters for Bloomberg look
        table_lines = table.split('\n')
        formatted_table = []
        
        # Top border
        formatted_table.append("┌" + "─" * (len(table_lines[0]) + 2) + "┐")
        
        # Add table content with side borders
        for line in table_lines:
            formatted_table.append(f"│ {line:<{len(table_lines[0])}} │")
        
        # Bottom border
        formatted_table.append("└" + "─" * (len(table_lines[0]) + 2) + "┘")
        
        return header + "\n".join(formatted_table)
    
    def create_compact_table(self, currency_pair: str = "EURUSD", tenor: str = "1M") -> pd.DataFrame:
        """Create a compact DataFrame suitable for display or export"""
        
        # Get volatility surface data
        df = self.client.get_fx_volatility_surface(currency_pair, tenor)
        
        # Pivot to create a more compact view
        # Separate ATM
        atm_value = df[df["Product"] == "ATM"]["Mid"].iloc[0]
        
        # Create Risk Reversal and Butterfly columns
        rr_data = df[df["Product"] == "RR"].set_index("Delta")["Mid"]
        bf_data = df[df["Product"] == "BF"].set_index("Delta")["Mid"]
        
        # Combine into single DataFrame
        compact_df = pd.DataFrame({
            "Risk_Reversal": rr_data,
            "ATM": atm_value,
            "Butterfly": bf_data
        })
        
        # Add bid/ask data
        rr_bid = df[df["Product"] == "RR"].set_index("Delta")["Bid"]
        rr_ask = df[df["Product"] == "RR"].set_index("Delta")["Ask"]
        bf_bid = df[df["Product"] == "BF"].set_index("Delta")["Bid"]
        bf_ask = df[df["Product"] == "BF"].set_index("Delta")["Ask"]
        atm_bid = df[df["Product"] == "ATM"]["Bid"].iloc[0]
        atm_ask = df[df["Product"] == "ATM"]["Ask"].iloc[0]
        
        compact_df["RR_Bid"] = rr_bid
        compact_df["RR_Ask"] = rr_ask
        compact_df["ATM_Bid"] = atm_bid
        compact_df["ATM_Ask"] = atm_ask
        compact_df["BF_Bid"] = bf_bid
        compact_df["BF_Ask"] = bf_ask
        
        return compact_df
    
    def display_surface_summary(self, currency_pair: str = "EURUSD", tenor: str = "1M"):
        """Display a summary of the volatility surface with key metrics"""
        
        df = self.client.get_fx_volatility_surface(currency_pair, tenor)
        
        print(f"\n{'='*60}")
        print(f"FX VOLATILITY SURFACE SUMMARY")
        print(f"{currency_pair} {tenor} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # ATM Volatility
        atm = df[df["Product"] == "ATM"].iloc[0]
        print(f"ATM Volatility: {atm['Mid']:.3f}% (Bid: {atm['Bid']:.3f}%, Ask: {atm['Ask']:.3f}%)")
        print(f"ATM Spread: {atm['Ask'] - atm['Bid']:.3f}%\n")
        
        # Risk Reversal Summary
        print("Risk Reversals:")
        for _, row in df[df["Product"] == "RR"].iterrows():
            sign = "+" if row["Mid"] > 0 else ""
            print(f"  {row['Delta']}: {sign}{row['Mid']:.3f}% (Spread: {row['Ask'] - row['Bid']:.3f}%)")
        
        print("\nButterflies:")
        for _, row in df[df["Product"] == "BF"].iterrows():
            print(f"  {row['Delta']}: {row['Mid']:.3f}% (Spread: {row['Ask'] - row['Bid']:.3f}%)")
        
        print(f"\n{'='*60}")


def main():
    """Example usage"""
    # Initialize client
    client = BloombergAPIClient()
    
    # Create table display
    table_display = VolatilitySurfaceTable(client)
    
    # Display Bloomberg-style table
    print(table_display.create_bloomberg_style_table("EURUSD", "1M"))
    
    # Display summary
    table_display.display_surface_summary("EURUSD", "1M")
    
    # Get compact DataFrame
    compact_df = table_display.create_compact_table("EURUSD", "1M")
    print("\nCompact DataFrame:")
    print(compact_df)


if __name__ == "__main__":
    main()