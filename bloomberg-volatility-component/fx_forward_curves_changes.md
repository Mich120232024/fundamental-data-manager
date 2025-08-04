# FX Forward Curves Tab - Key Changes

## Original Approach
- Called non-existent endpoint: `/api/fx-forwards/curves`
- Expected backend to do all calculations
- Limited to 3Y data

## New Approach (Using Generic Bloomberg API)
- Uses existing `/api/bloomberg/reference` endpoint
- Fetches all tickers in one batch request
- Supports up to 5Y data (using the 4Y/5Y tickers we added)

## Key Changes in fetchForwardData():

```typescript
// OLD: Custom endpoint
const response = await fetch(`${apiUrl}/api/fx-forwards/curves`, {
  method: 'POST',
  body: JSON.stringify({
    currency_pairs: Array.from(selectedPairs),
    display_mode: "outright",
    max_tenor: "5Y"
  })
})

// NEW: Generic Bloomberg reference endpoint
const securities: string[] = [
  `${pair} Curncy`, // Spot rate
  ...tenors.map(tenor => `${pair}${tenor} Curncy`) // Forward rates up to 5Y
]

const response = await fetch(`${apiUrl}/api/bloomberg/reference`, {
  method: 'POST',
  body: JSON.stringify({
    securities: securities,
    fields: ['PX_LAST', 'PX_BID', 'PX_ASK']
  })
})
```

## Data Processing
- Calculates forward outright rates from Bloomberg forward points
- Handles different pip conventions (USD/JPY vs others)
- Calculates implied yield differentials
- All processing done in the frontend

## To Apply Changes
Replace the existing FXForwardCurvesTab.tsx with FXForwardCurvesTab_updated.tsx