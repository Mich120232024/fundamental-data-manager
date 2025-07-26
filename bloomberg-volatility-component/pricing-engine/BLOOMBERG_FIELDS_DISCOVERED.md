# Bloomberg Fields for FX Options Pricing

## Working Bloomberg Tickers Discovered

### 1. Spot Rates
```
EURUSD Curncy - Returns PX_LAST, PX_BID, PX_ASK
```

### 2. Forward Points
```
EURUSD1M Curncy - Returns forward points directly as PX_LAST, PX_BID, PX_ASK
EURUSD2M Curncy - Similar format for other tenors
```
Note: The values returned (e.g., 24.3) are forward points in pips

### 3. Interest Rates

#### Deposit Rates (Tomorrow/Next)
```
USDR1T Curncy - USD deposit rate (4.375%)
EUDR1T Curncy - EUR deposit rate (1.975%)
```

#### Money Market Rates
```
US0001M Index - USD 1-month rate (4.96018%)
EUR001M Index - EUR 1-month rate (1.904%)
```

### 4. Volatility Data (Already Working)
```
EURUSDV1M BGN Curncy - ATM volatility
EURUSD25R1M BGN Curncy - 25-delta risk reversal
EURUSD25B1M BGN Curncy - 25-delta butterfly
```

## Failed Tickers (Don't Exist)
- EURUSD1M FWD Curncy
- USD DEPO 1M Curncy
- EUR DEPO 1M Curncy
- USDOIS Index
- USDSOFR Index
- SOFR Index

## Next Steps
1. Wait for RESEARCH_001's mathematical models
2. Implement forward rate calculation: Spot + (Forward Points / 10000)
3. Create interest rate curve interpolation
4. Build pricing service once formulas are ready