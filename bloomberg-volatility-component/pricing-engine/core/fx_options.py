"""
FX Options Pricing Engine - Garman-Kohlhagen Implementation
Follows RESEARCH_001's technical specification for production FX options pricing
"""
import math
from typing import Dict, Optional, Union
from scipy.stats import norm
from dataclasses import dataclass, asdict
from datetime import datetime, date
import numpy as np


@dataclass
class OptionSpec:
    """Option specification as per RESEARCH_001 spec"""
    currency_pair: str
    option_type: str  # "call" or "put"
    strike_price: Optional[float] = None
    target_delta: Optional[float] = None
    notional: float = 1_000_000
    expiry_date: date = None
    volatility_type: str = "smile"  # "atm" or "smile"
    delta_type: str = "spot"  # "spot", "forward", "premium_adjusted"
    calculation_date: date = None


@dataclass
class MarketData:
    """Market data structure matching Bloomberg API"""
    spot_rate: float
    domestic_rate: float  # USD rate (continuous)
    foreign_rate: float   # EUR rate (continuous)
    volatility: float     # Annualized volatility
    forward_rate: Optional[float] = None


@dataclass
class PricingResult:
    """Complete pricing result with Greeks"""
    price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho_domestic: float
    rho_foreign: float
    
    # Additional metadata
    strike_used: float
    volatility_used: float
    time_to_expiry: float
    forward_rate: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FXOptionsEngine:
    """
    Production FX Options Pricing Engine
    Implements Garman-Kohlhagen model as specified by RESEARCH_001
    """
    
    def __init__(self):
        self.DAYS_PER_YEAR = 365.25
        
    def calculate_time_to_expiry(self, expiry_date: date, calc_date: date = None) -> float:
        """Calculate time to expiry in years using ACT/365.25"""
        if calc_date is None:
            calc_date = date.today()
        
        days_to_expiry = (expiry_date - calc_date).days
        return max(days_to_expiry / self.DAYS_PER_YEAR, 1e-8)  # Min time to avoid div by zero
    
    def calculate_forward_rate(self, spot: float, domestic_rate: float, 
                             foreign_rate: float, time_to_expiry: float) -> float:
        """Calculate forward rate: F = S * exp((rd - rf) * T)"""
        return spot * math.exp((domestic_rate - foreign_rate) * time_to_expiry)
    
    def calculate_strike_from_delta(self, target_delta: float, spot: float, 
                                  domestic_rate: float, foreign_rate: float,
                                  volatility: float, time_to_expiry: float,
                                  option_type: str) -> float:
        """
        Calculate strike price from target delta using Newton-Raphson
        Uses spot delta as specified by RESEARCH_001
        """
        # Initial guess: ATM strike
        strike = spot
        
        for _ in range(10):  # Newton-Raphson iterations
            result = self._price_option_core(
                spot, strike, domestic_rate, foreign_rate, 
                volatility, time_to_expiry, option_type == "call"
            )
            
            delta_diff = result.delta - target_delta
            if abs(delta_diff) < 1e-6:
                break
                
            # Newton-Raphson update: K_new = K_old - f(K)/f'(K)
            # f'(K) = -gamma (derivative of delta w.r.t. strike)
            strike = strike + delta_diff / result.gamma
            
        return strike
    
    def build_smile_volatility(self, vol_data: Dict, target_delta_or_strike: Union[float, None] = None) -> float:
        """
        Convert Bloomberg RR/BF data to actual volatility
        Implements RESEARCH_001's Bloomberg conversion formulas
        """
        try:
            # Extract Bloomberg volatility data (assuming percentages)
            atm_vol = (vol_data.get('atm_bid', 0) + vol_data.get('atm_ask', 0)) / 2 / 100
            rr_25d = (vol_data.get('rr_25d_bid', 0) + vol_data.get('rr_25d_ask', 0)) / 2 / 100
            bf_25d = (vol_data.get('bf_25d_bid', 0) + vol_data.get('bf_25d_ask', 0)) / 2 / 100
            
            # Bloomberg standard conversion
            vol_25d_call = atm_vol + bf_25d + 0.5 * rr_25d
            vol_25d_put = atm_vol + bf_25d - 0.5 * rr_25d
            
            # For now, return ATM volatility
            # TODO: Implement full smile interpolation based on target delta/strike
            return atm_vol
            
        except Exception as e:
            raise ValueError(f"Failed to build smile volatility: {e}")
    
    def _price_option_core(self, spot: float, strike: float, domestic_rate: float,
                          foreign_rate: float, volatility: float, time_to_expiry: float,
                          is_call: bool) -> PricingResult:
        """
        Core Garman-Kohlhagen pricing implementation
        All Greeks calculated analytically for precision
        """
        # Handle edge cases
        if time_to_expiry <= 0:
            intrinsic = max(0, (spot - strike) if is_call else (strike - spot))
            return PricingResult(
                price=intrinsic, delta=0, gamma=0, vega=0, theta=0,
                rho_domestic=0, rho_foreign=0, strike_used=strike,
                volatility_used=volatility, time_to_expiry=0,
                forward_rate=spot
            )
        
        # Standard Garman-Kohlhagen calculations
        sqrt_t = math.sqrt(time_to_expiry)
        d1 = (math.log(spot / strike) + (domestic_rate - foreign_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * sqrt_t)
        d2 = d1 - volatility * sqrt_t
        
        # Standard normal CDF and PDF
        nd1 = norm.cdf(d1)
        nd2 = norm.cdf(d2)
        n_d1 = norm.pdf(d1)
        
        # Forward rate for metadata
        forward = self.calculate_forward_rate(spot, domestic_rate, foreign_rate, time_to_expiry)
        
        # Discount factors
        df_domestic = math.exp(-domestic_rate * time_to_expiry)
        df_foreign = math.exp(-foreign_rate * time_to_expiry)
        
        if is_call:
            # Call option
            price = spot * df_foreign * nd1 - strike * df_domestic * nd2
            delta = df_foreign * nd1
            rho_domestic = -strike * time_to_expiry * df_domestic * nd2
            rho_foreign = spot * time_to_expiry * df_foreign * nd1
        else:
            # Put option  
            price = strike * df_domestic * norm.cdf(-d2) - spot * df_foreign * norm.cdf(-d1)
            delta = -df_foreign * norm.cdf(-d1)
            rho_domestic = strike * time_to_expiry * df_domestic * norm.cdf(-d2)
            rho_foreign = -spot * time_to_expiry * df_foreign * norm.cdf(-d1)
        
        # Greeks (same for calls and puts)
        gamma = df_foreign * n_d1 / (spot * volatility * sqrt_t)
        vega = spot * df_foreign * n_d1 * sqrt_t / 100  # Per 1% vol change
        theta = (
            -spot * df_foreign * n_d1 * volatility / (2 * sqrt_t) 
            - foreign_rate * spot * df_foreign * (nd1 if is_call else -norm.cdf(-d1))
            + domestic_rate * strike * df_domestic * (nd2 if is_call else -norm.cdf(-d2))
        ) / 365  # Per day
        
        return PricingResult(
            price=price,
            delta=delta, 
            gamma=gamma,
            vega=vega,
            theta=theta,
            rho_domestic=rho_domestic,
            rho_foreign=rho_foreign,
            strike_used=strike,
            volatility_used=volatility,
            time_to_expiry=time_to_expiry,
            forward_rate=forward
        )
    
    def price_option(self, option_spec: OptionSpec, market_data: MarketData) -> PricingResult:
        """
        Main pricing method - handles all option specification types
        """
        # Calculate time to expiry
        calc_date = option_spec.calculation_date or date.today()
        time_to_expiry = self.calculate_time_to_expiry(option_spec.expiry_date, calc_date)
        
        # Determine strike price
        if option_spec.strike_price is not None:
            strike = option_spec.strike_price
        elif option_spec.target_delta is not None:
            strike = self.calculate_strike_from_delta(
                option_spec.target_delta,
                market_data.spot_rate,
                market_data.domestic_rate,
                market_data.foreign_rate,
                market_data.volatility,
                time_to_expiry,
                option_spec.option_type
            )
        else:
            raise ValueError("Must specify either strike_price or target_delta")
        
        # Price the option
        result = self._price_option_core(
            market_data.spot_rate,
            strike,
            market_data.domestic_rate,
            market_data.foreign_rate,
            market_data.volatility,
            time_to_expiry,
            option_spec.option_type == "call"
        )
        
        # Scale by notional
        result.price *= option_spec.notional
        result.delta *= option_spec.notional
        result.gamma *= option_spec.notional
        result.vega *= option_spec.notional
        result.theta *= option_spec.notional
        result.rho_domestic *= option_spec.notional
        result.rho_foreign *= option_spec.notional
        
        return result


def create_pricing_engine() -> FXOptionsEngine:
    """Factory function for pricing engine"""
    return FXOptionsEngine()