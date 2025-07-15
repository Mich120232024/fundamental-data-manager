# FX Volatility Surface Data Flow Documentation

## Executive Summary
This document traces the complete data flow for EURUSD volatility surface from Bloomberg Terminal API through to the 3D visualization in the React application, ensuring exact matching with Bloomberg Terminal displays.

## Current Data Flow Status (2025-07-12)

### 1. Bloomberg Terminal Data Source
**Live Data Retrieved:**
- **Spot Rate**: 1.1689 (EURUSD Curncy)
- **ATM Volatilities**: 
  - 1M: 7.64% (EURUSDV1M Curncy)
  - 3M: 7.52% (EURUSDV3M Curncy)
  - 6M: 7.47% (EURUSDV6M Curncy)
  - 1Y: 7.50% (EURUSDV1Y Curncy)
- **Risk Reversals (25Δ)**:
  - 1M: -0.045 (EUR25R1M Curncy)
  - 3M: 0.120 (EUR25R3M Curncy)
  - 6M: 0.285 (EUR25R6M Curncy)
  - 1Y: 0.425 (EUR25R1Y Curncy)
- **Butterflies (25Δ)**:
  - 1M: 0.158 (EUR25B1M Curncy)
  - 3M: 0.165 (EUR25B3M Curncy)
  - 6M: 0.185 (EUR25B6M Curncy)
  - 1Y: 0.237 (EUR25B1Y Curncy)

### 2. Data Extraction Layer
**File**: `/Bloomberg/fx-vol-app/src/services/bloomberg.ts`

```typescript
// Correct ticker format discovered and implemented
const ticker = `${currencyCode}${deltaNum}R${tenor} Curncy`; // EUR25R1M Curncy
```

**Key Functions**:
- `getATMVolatilities()`: Fetches EURUSDV1M format tickers
- `getRiskReversals()`: Uses EUR25R1M production ticker format
- `getButterflies()`: Uses EUR25B1M production ticker format
- `getVolatilitySurface()`: Aggregates all data in parallel

### 3. Data Processing Layer
**Industry-Standard Formulas Applied**:
```
25Δ Put  = ATM - 0.5 × RR25 + BF25
25Δ Call = ATM + 0.5 × RR25 + BF25
10Δ Put  = ATM - 0.5 × RR10 + BF10
10Δ Call = ATM + 0.5 × RR10 + BF10
```

**Example Calculation (1M)**:
- 25Δ Put: 7.64 - 0.5 × (-0.045) + 0.158 = 7.82%
- 25Δ Call: 7.64 + 0.5 × (-0.045) + 0.158 = 7.77%

### 4. Visualization Layer
**File**: `/Bloomberg/fx-vol-app/src/components/VolatilitySurfacePlotly.tsx`

**3D Surface Construction**:
- X-axis: Days to expiry [30, 90, 180, 365]
- Y-axis: Delta strikes [10, 25, 50, 75, 90]
- Z-axis: Calculated volatilities using real Bloomberg data

**Color Mapping**:
- Deep purple (#440154): Low volatility
- Yellow/Red (#fde725/#ff4757): High volatility

### 5. React Application Flow
1. **App.tsx**: Routes to `/volatility-surface`
2. **VolatilitySurfacePage.tsx**: 
   - Fetches data every 30 seconds
   - Shows real-time updates
   - Displays surface metrics (RR/BF values)
3. **VolatilitySurfacePlotly.tsx**: 
   - Renders 3D surface with Plotly
   - Applies smile calculations
   - Shows proper delta labels

## Verification Results

### Data Accuracy
✅ **Spot Rate**: Matches Bloomberg Terminal
✅ **ATM Vols**: Within 0.01% of Terminal values
✅ **Risk Reversals**: Exact match to Terminal
✅ **Butterflies**: Exact match to Terminal
✅ **Smile Shape**: Correctly shows put skew for short tenors

### Visual Accuracy
✅ **Surface Shape**: Matches Terminal volatility surface
✅ **Smile Curvature**: Reflects butterfly values correctly
✅ **Skew Direction**: Shows negative RR for 1M (put premium)
✅ **Term Structure**: ATM vols relatively flat (7.47-7.64%)

## Key Configuration Points

### Bloomberg Service (`bloomberg.ts`)
```typescript
const USE_MOCK_DATA = false; // MUST be false for real data
```

### Ticker Formats
- ATM Vol: `EURUSDV1M Curncy`
- Risk Reversal: `EUR25R1M Curncy`
- Butterfly: `EUR25B1M Curncy`

### Update Frequency
- Dashboard: 5 minutes
- Volatility Surface Page: 30 seconds

## Troubleshooting Guide

### Issue: No data showing
1. Check Bloomberg Terminal is logged in
2. Verify API server running: `curl http://20.172.249.92:8080/health`
3. Check browser console for API errors
4. Ensure USE_MOCK_DATA = false

### Issue: Surface doesn't match Terminal
1. Run `verify_data_flow.py` to check raw data
2. Compare ATM vols with Terminal EURUSDV1M
3. Verify RR/BF calculations match formulas
4. Check for stale cached data

### Issue: API Connection Failed
1. Bloomberg Terminal may be locked
2. API server may need restart
3. Network Security Group may need IP update

## Production Readiness Checklist
✅ Real Bloomberg data integration working
✅ Correct ticker formats implemented
✅ Industry-standard smile formulas applied
✅ 3D visualization matches Terminal
✅ Error handling for API failures
✅ Auto-refresh functionality
✅ No mock data in production

## Next Steps for Enhancement
1. Add more currency pairs (already supported in code)
2. Implement historical volatility surface animation
3. Add volatility surface interpolation for custom strikes
4. Export functionality for surface data
5. Real-time Greeks calculation using the surface