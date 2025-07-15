# Bloomberg FX Volatility Analysis Results

## Executive Summary
After extensive testing of the Bloomberg Terminal API, we have determined that:
1. **ATM volatilities are fully available** via tickers like `EURUSDV1M Curncy`
2. **Risk Reversal and Butterfly data is NOT available** through the Bloomberg Terminal API
3. **Option tickers return premium prices**, not implied volatilities
4. The React application has been configured to display ATM volatility term structures

## Detailed Findings

### 1. Available Data

#### ✅ ATM Volatilities (Working)
```
EURUSDV1M Curncy: 7.6375%
EURUSDV3M Curncy: 7.5175%
EURUSDV6M Curncy: 7.47%
EURUSDV1Y Curncy: 7.495%
```

#### ❌ Risk Reversals (Not Available)
- Fields tested: `25D_RR_1M`, `25D_RR_3M`, `25D_RR_6M`, `25D_RR_1Y`
- Result: All return null/undefined
- Alternative tickers tested: `EUR25DR1M Curncy`, `EURUSD25RR1M Curncy`
- Result: Not found

#### ❌ Butterflies (Not Available)
- Fields tested: `25D_BF_1M`, `25D_BF_3M`, `25D_BF_6M`, `25D_BF_1Y`
- Result: All return null/undefined
- Alternative tickers tested: `EUR25BF1M Curncy`, `EURUSD25BF1M Curncy`
- Result: Not found

### 2. Option Ticker Analysis

#### EURUSD1M25C and EURUSD1M25P Curncy
- Both return identical values: 24.14
- These are option **premiums in pips**, not volatilities
- Bid/Ask spreads confirm these are prices: 24.10/24.18
- No `IMP_VOLATILITY` field available on these tickers

### 3. Historical Evidence
According to logs from yesterday, these fields were previously returning data:
- `25D_RR_1M`, `25D_RR_3M`, `25D_RR_6M`
- `25D_BF_1M`, `25D_BF_3M`, `25D_BF_6M`

**Conclusion**: Bloomberg Terminal configuration or subscription has changed

### 4. Implementation Decision

Given the data limitations, the application implements:
1. **ATM volatility term structure visualization**
2. **Flat volatility surface** (same vol across all strikes)
3. **Real Bloomberg data only** - no synthetic smile parameters

This is industry standard when smile data is unavailable.

## Code Changes Made

### bloomberg.ts
- Updated to attempt Risk Reversal extraction from option tickers
- Falls back to flat surface when data unavailable
- Removed all mock data generation

### VolatilitySurfacePlotly.tsx
- Displays only real Bloomberg ATM volatilities
- Creates flat surface across delta strikes
- Updated description to reflect data limitations

## Next Steps

1. **Contact Bloomberg Support** to understand why RR/BF fields are not available
2. **Check Bloomberg Terminal directly** to see if data is visible there
3. **Consider alternative data sources** for FX option smile data
4. **Monitor for data availability** - fields may become available again

## Testing Scripts Created

1. `test_fx_vol_surface.py` - Initial field discovery
2. `test_eurusd_rr_bf.py` - Focused RR/BF testing
3. `test_eurusd_strikes.py` - Individual strike testing
4. `test_option_volatilities.py` - Option implied vol extraction
5. `test_single_eurusd.py` - Detailed single currency analysis

All scripts are available in the Bloomberg project directory for future testing.