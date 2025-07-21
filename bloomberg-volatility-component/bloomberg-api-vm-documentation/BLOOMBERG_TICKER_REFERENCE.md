# Bloomberg Ticker Reference Guide

## FX SPOT & FORWARDS
```
EURUSD Curncy                    # Spot
EURUSD1W Curncy                  # 1-week forward
EURUSD1M Curncy                  # 1-month forward
EURUSD12M Curncy                 # 12-month forward
```

## FX OPTIONS
Format: `[CCY][Tenor][Strike/Delta][Type] BGN Curncy`

```
EUR1W25C BGN Curncy              # 1-week 25-delta call
EUR1M25P BGN Curncy              # 1-month 25-delta put
EUR3MATM BGN Curncy              # 3-month at-the-money
EUR1Y25R BGN Curncy              # 1-year 25-delta risk reversal
EUR6M25B BGN Curncy              # 6-month 25-delta butterfly
```

### Key Components:
- **Tenors**: ON(overnight), 1W, 2W, 3W, 1M, 2M... 1Y, 2Y...
- **Deltas**: 10, 15, 25, 35, 40, ATM
- **Types**: C(call), P(put), R(risk reversal), B(butterfly), S(strangle)

## FX VOLATILITIES
```
EURUSDV1M BGN Curncy             # 1-month ATM vol
EURUSDV1M25C BGN Curncy          # 1-month 25-delta call vol
EURUSDV3M25R BGN Curncy          # 3-month 25-delta RR vol
```

## VOLATILITY SURFACE TICKERS (Our Use Case)

### ATM Volatility
- Format: `[PAIR]V[TENOR] BGN Curncy` or `[PAIR]V[TENOR] Curncy` (for ON)
- Examples:
  - `EURUSDVON Curncy` - Overnight ATM vol
  - `EURUSDV1W BGN Curncy` - 1-week ATM vol
  - `EURUSDV1M BGN Curncy` - 1-month ATM vol

### Risk Reversals (25-delta)
- Format: `[PAIR][DELTA]R[TENOR] BGN Curncy`
- Examples:
  - `EURUSD25RON BGN Curncy` - Overnight 25-delta RR
  - `EURUSD25R1W BGN Curncy` - 1-week 25-delta RR
  - `EURUSD25R1M BGN Curncy` - 1-month 25-delta RR

### Butterflies (25-delta)
- Format: `[PAIR][DELTA]B[TENOR] BGN Curncy`
- Examples:
  - `EURUSD25BON BGN Curncy` - Overnight 25-delta BF
  - `EURUSD25B1W BGN Curncy` - 1-week 25-delta BF
  - `EURUSD25B1M BGN Curncy` - 1-month 25-delta BF

### Short-Dated Options (1D, 2D, 3D)
Based on the FX OPTIONS format above, these should be:
- `EUR1D25R BGN Curncy` - 1-day 25-delta risk reversal
- `EUR2D25R BGN Curncy` - 2-day 25-delta risk reversal
- `EUR3D25R BGN Curncy` - 3-day 25-delta risk reversal

Note: These may require specific Bloomberg data subscriptions.

## EQUITIES
```
AAPL US Equity                   # US stocks
VOD LN Equity                    # London
7203 JT Equity                   # Tokyo
```

## EQUITY OPTIONS
```
AAPL US 01/20/23 C150 Equity     # AAPL Jan 2023 $150 Call
SPX US 12/15/23 P4000 Equity     # S&P 500 Put
```

## BONDS
Corporate: `[Ticker] [Coupon] [Maturity] Corp`
```
AAPL 3.45 02/09/45 Corp          # Apple bond
T 2.5 05/15/30 Govt              # US Treasury
```

## COMMODITIES
```
CL1 Comdty                       # WTI front month
CLZ3 Comdty                      # WTI Dec 2023
GC1 Comdty                       # Gold front month
```

## INDICES
```
SPX Index                        # S&P 500
DXY Index                        # Dollar Index
VIX Index                        # Volatility Index
```

## RATES
```
USGG10YR Index                   # US 10Y yield
USSW10 Curncy                    # USD 10Y swap
EUSA10 Curncy                    # EUR 10Y swap
```

## ADDING FIELDS
For specific data fields, append:
```
[Ticker] BID                     # Bid price
[Ticker] ASK                     # Ask price
[Ticker] MID                     # Mid price
[Ticker] VOLUME                  # Volume
[Ticker] PX_LAST                 # Last price
```

## BLOOMBERG DATA FORMULAS (Excel/API)

### Real-time data
```
=BDP("EURUSD Curncy", "BID")
=BDP("EUR1M25R BGN Curncy", "PX_LAST")
```

### Historical data
```
=BDH("EURUSD Curncy", "PX_LAST", "1/1/2024", "12/31/2024")
```

### Bulk data
```
=BDS("AAPL US Equity", "DVD_HIST")
```

## KEY SHORTCUTS FOR DISCOVERY
- `SECF <GO>` - Security finder
- `TKR <GO>` - Ticker lookup
- `FLDS <GO>` - All available fields
- `DOCS TICKER <GO>` - Full documentation

---

*Last Updated: January 21, 2025*
*Source: Bloomberg Terminal Documentation*