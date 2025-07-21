# Bloomberg Ticker Format Guide - Critical Information

## Short-Dated Options (CRITICAL FIX)

### ❌ WRONG Format (Returns no data)
```
EURUSDV1D BGN Curncy  ❌ - Invalid ticker format
EURUSDV2D BGN Curncy  ❌ - Invalid ticker format
EURUSDV3D BGN Curncy  ❌ - Invalid ticker format
```

### ✅ CORRECT Bloomberg Format (But data availability varies)
```
EURUSDVON BGN Curncy  ✅  - Overnight (O/N) - HAS DATA
EURUSDVTN BGN Curncy  ⚠️  - Tomorrow Next (T/N) - Valid ticker but NO DATA
EURUSDVSN BGN Curncy  ⚠️  - Spot Next (S/N) - Valid ticker but NO DATA
```

### Important Note
While TN and SN are valid Bloomberg tickers (API returns success: true), they return empty data fields. This is normal - Bloomberg typically only provides quotes for ON (overnight) and longer tenors in the FX options market.

## Complete Tenor Mapping

| Display | Wrong | Correct | Description |
|---------|-------|---------|-------------|
| O/N | 1D | ON | Overnight |
| T/N | 2D | TN | Tomorrow Next |
| S/N | 3D | SN | Spot Next |
| 1W | 1W | 1W | 1 Week ✓ |
| 2W | 2W | 2W | 2 Weeks ✓ |
| 3W | 3W | 3W | 3 Weeks ✓ |
| 1M | 1M | 1M | 1 Month ✓ |
| 2M | 2M | 2M | 2 Months ✓ |
| 3M | 3M | 3M | 3 Months ✓ |
| 6M | 6M | 6M | 6 Months ✓ |
| 9M | 9M | 9M | 9 Months ✓ |
| 1Y | 1Y | 1Y | 1 Year ✓ |
| 18M | 18M | 18M | 18 Months ✓ |
| 2Y | 2Y | 2Y | 2 Years ✓ |

## Working Examples (Verified)

### Overnight Options
```bash
# ATM Volatility
EURUSDVON BGN Curncy → 8.855% (Bid: 7.04%, Ask: 10.67%)

# Risk Reversals
EURUSD5RON BGN Curncy → 0.8325% (Bid: -2.98%, Ask: 4.645%)
EURUSD10RON BGN Curncy → 0.6725% (Bid: -1.505%, Ask: 2.85%)
EURUSD15RON BGN Curncy → 0.55% (Bid: -1.175%, Ask: 2.275%)
EURUSD25RON BGN Curncy → 0.355% (Bid: -0.915%, Ask: 1.625%)
EURUSD35RON BGN Curncy → 0.2% (Bid: -0.89%, Ask: 1.29%)

# Butterflies
EURUSD5BON BGN Curncy → 0.7025% (Bid: -1.84%, Ask: 3.245%)
EURUSD10BON BGN Curncy → 0.4925% (Bid: -0.96%, Ask: 1.945%)
EURUSD15BON BGN Curncy → 0.36% (Bid: -0.82%, Ask: 1.54%)
EURUSD25BON BGN Curncy → 0.1775% (Bid: -0.73%, Ask: 1.085%)
EURUSD35BON BGN Curncy → 0.065% (Bid: -0.715%, Ask: 0.845%)
```

## Pattern Summary

### ATM Volatility
```
{PAIR}V{TENOR} BGN Curncy
```
- TENOR: ON, TN, SN, 1W, 2W, 3W, 1M, 2M, 3M, 6M, 9M, 1Y, 18M, 2Y

### Risk Reversals (Single R)
```
{PAIR}{DELTA}R{TENOR} BGN Curncy
```
- DELTA: 5, 10, 15, 25, 35
- TENOR: ON, TN, SN, 1W, 2W, 3W, 1M, 2M, 3M, 6M, 9M, 1Y, 18M, 2Y

### Butterflies (Single B)
```
{PAIR}{DELTA}B{TENOR} BGN Curncy
```
- DELTA: 5, 10, 15, 25, 35
- TENOR: ON, TN, SN, 1W, 2W, 3W, 1M, 2M, 3M, 6M, 9M, 1Y, 18M, 2Y

## Common Mistakes to Avoid

1. **Using 1D/2D/3D instead of ON/TN/SN** - This is the most common error
2. **Using double letters (RR/BF) instead of single (R/B)**
3. **Missing "BGN Curncy" suffix**
4. **Using slashes in tenors (O/N, T/N) instead of ON, TN**

## Testing New Tickers

Always test unknown tickers with the generic endpoint first:
```bash
curl -X POST http://20.172.249.92:8080/api/bloomberg/reference \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{
    "securities": ["YOUR_TICKER_HERE"],
    "fields": ["PX_LAST", "PX_BID", "PX_ASK"]
  }'
```

---

*Last Updated: January 20, 2025*
*Critical Fix: Short-dated option tenor formats*