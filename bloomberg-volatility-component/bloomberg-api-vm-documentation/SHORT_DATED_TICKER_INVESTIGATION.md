# Short-Dated (1D/2D/3D) Ticker Investigation Results

## Summary
After extensive testing on the Bloomberg VM, I found that the 1D/2D/3D volatility tickers are **not available** in our Bloomberg Terminal data subscription. Instead, Bloomberg uses ON (Overnight), TN (Tomorrow/Next), and SN (Spot/Next) for very short-dated options.

## Test Results

### What Works
- **ON (Overnight)** volatility data is available:
  - `EURUSDVON Curncy` - ATM volatility (PX_LAST: 8.965)
  - `EURUSD25RON BGN Curncy` - 25-delta risk reversal (PX_LAST: 0.365)
  - Full bid/ask spreads available

### What Doesn't Work
- **TN and SN** tickers exist but return no price data (empty fields)
- **1D/2D/3D format** returns "Unknown/Invalid Security" errors for all variations tested:
  - `EUR1D25R BGN Curncy` - Invalid
  - `EURUSD1DV BGN Curncy` - Invalid
  - `EURUSDV1D BGN Curncy` - Invalid

### Misleading Results
- `EURUSD1D BGN Curncy` returns data but it's FX forwards, not volatility:
  - EURUSD1D = "EURO O/N" (overnight forward)
  - EURUSD2D = "EURO T/N" (tomorrow/next forward)
  - EURUSD3D = "EURO S/N" (spot/next forward)

## Conclusion
The application correctly shows ON (overnight) data. The 1D/2D/3D tickers mentioned by the user likely require:
1. A different Bloomberg data subscription/license
2. Or use a different ticker format not documented in standard references
3. Or are available only in specific markets/times

## Current Implementation
The app already includes ON in STANDARD_TENORS and handles it correctly with special formatting (no BGN suffix for ATM).

## Recommendation
Continue using ON as the shortest tenor. If TN/SN data becomes available in the future, they can be added to STANDARD_TENORS array.