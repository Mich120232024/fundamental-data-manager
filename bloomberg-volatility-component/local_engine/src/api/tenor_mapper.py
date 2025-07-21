"""
Tenor mapping utilities for Bloomberg volatility data
"""

# Standard FX option tenors up to 2 years
STANDARD_TENORS = [
    "1D",   # 1 day (overnight)
    "1W",   # 1 week
    "2W",   # 2 weeks
    "3W",   # 3 weeks
    "1M",   # 1 month
    "2M",   # 2 months
    "3M",   # 3 months
    "4M",   # 4 months
    "5M",   # 5 months
    "6M",   # 6 months
    "9M",   # 9 months
    "1Y",   # 1 year
    "15M",  # 15 months
    "18M",  # 18 months
    "2Y"    # 2 years
]

# Map tenors to approximate days for sorting
TENOR_DAYS = {
    "1D": 1,
    "1W": 7,
    "2W": 14,
    "3W": 21,
    "1M": 30,
    "2M": 60,
    "3M": 90,
    "4M": 120,
    "5M": 150,
    "6M": 180,
    "9M": 270,
    "1Y": 365,
    "15M": 450,
    "18M": 540,
    "2Y": 730
}

def get_tenor_order(tenor: str) -> int:
    """Get sorting order for tenor"""
    return TENOR_DAYS.get(tenor, 999)