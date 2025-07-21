# Bloomberg Volatility Surface Component

A real-time FX options volatility surface visualization tool that connects to Bloomberg Terminal data via Azure VM.

## Overview

This React + TypeScript application displays real-time FX options volatility surfaces with data sourced directly from Bloomberg Terminal. It shows ATM volatilities, risk reversals, and butterflies across multiple deltas (5D, 10D, 15D, 25D, 35D) and tenors.

## Features

- **Dual View Modes**:
  - **Volatility Surface**: Real-time grid view of current market volatilities
  - **Historical Analysis**: Time series table showing volatility evolution
- **Real-time Bloomberg Data**: Live volatility surface data from Bloomberg Terminal
- **Multiple Data Modes**: Live, EOD (End of Day), and Historical data views
- **28 Currency Pairs**: All major FX pairs supported
- **Full Delta Coverage**: 5D, 10D, 15D, 25D, 35D for both risk reversals and butterflies
- **Bid/Ask Spreads**: Complete bid/ask pricing for all volatility components
- **Historical Date Ranges**: 7 days to 2 years of historical data
- **Tab Navigation**: Easy switching between Surface and Historical views
- **Auto-refresh**: Configurable refresh intervals for live data
- **Dark/Light Themes**: Professional terminal-style themes

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│   React Frontend    │────▶│   Bloomberg API     │────▶│ Bloomberg Terminal│
│  (Vite + TypeScript)│     │  (Python FastAPI)   │     │   (Windows VM)   │
└─────────────────────┘     └─────────────────────┘     └──────────────────┘
         Port 3000               Port 8080                    Azure VM
```

## Bloomberg API Details

- **Endpoint**: http://20.172.249.92:8080
- **VM**: bloomberg-vm-02 in Azure (bloomberg-terminal-rg)
- **API File**: `C:\Bloomberg\APIServer\main_checkpoint_working_2025_07_16.py`

### Available Endpoints

- `GET /health` - API health check and status
- `POST /api/bloomberg/reference` - Real-time reference data
- `POST /api/bloomberg/historical` - Historical data with date range
- `GET /api/logs` - API request logs (debugging)

## Supported Tenors

```javascript
export const STANDARD_TENORS = [
  "ON",   // Overnight
  "1W",   // 1 week
  "2W",   // 2 weeks
  "3W",   // 3 weeks
  "1M",   // 1 month
  "2M",   // 2 months
  "3M",   // 3 months
  "4M",   // 4 months
  "6M",   // 6 months
  "9M",   // 9 months
  "1Y",   // 1 year
  "18M",  // 18 months
  "2Y"    // 2 years
]
```

## Bloomberg Ticker Format

### ATM Volatility
- Standard: `EURUSDV1M BGN Curncy`
- Overnight: `EURUSDVON Curncy` (no BGN)

### Risk Reversals
- Format: `[PAIR][DELTA]R[TENOR] BGN Curncy`
- Example: `EURUSD25R1M BGN Curncy`

### Butterflies
- Format: `[PAIR][DELTA]B[TENOR] BGN Curncy`
- Example: `EURUSD25B1M BGN Curncy`

## Development

### Prerequisites
- Node.js 18+
- Access to Bloomberg API VM (IP whitelisting required)
- Bloomberg Terminal data subscription

### Installation

```bash
cd gzc-volatility-surface
npm install
```

### Running Locally

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Building for Production

```bash
npm run build
```

## Key Components

### `MainAppContainer.tsx`
- Top-level container with tab navigation
- Manages switching between Surface and Historical views
- Consistent header and styling across views

### `VolatilitySurfaceContainer.tsx`
- Container for real-time volatility surface
- Handles data fetching and state management
- Implements date selection and currency pair switching
- Filters out empty tenors automatically

### `VolatilitySurfaceTable.tsx`
- Displays the volatility grid
- Color-codes risk reversals (green/red for positive/negative)
- Shows bid/ask spreads for all values

### `VolatilityHistoricalTable.tsx`
- Historical time series table view
- Configurable date ranges (7 days to 2 years)
- Tenor-specific analysis
- Shows evolution of ATM, RR, and BF values over time

### `bloomberg.ts`
- API client for Bloomberg data
- Handles authentication (Bearer token)
- Implements data parsing with regex for accurate matching
- Supports both live and historical data queries

## Important Notes

1. **Authentication**: API requires Bearer token authentication
2. **CORS**: Handled by the FastAPI backend
3. **Empty Data**: Tenors with no data are automatically filtered out
4. **Short-dated Options**: 1D/2D/3D tenors are not available in current Bloomberg subscription
5. **Data Refresh**: 
   - Live mode: Updates on demand
   - EOD mode: Shows previous day's closing data
   - Historical: Select any past date

## Troubleshooting

### "Bloomberg Disconnected"
- Check if API is running: `curl http://20.172.249.92:8080/health`
- Verify IP is whitelisted in Azure NSG rules
- Ensure correct API file is running on VM

### No Data Showing
- Check browser console for specific ticker errors
- Verify Bloomberg Terminal is logged in on VM
- Some tenors may not have data (especially short-dated)

### Historical Data Not Updating
- Check date format (YYYYMMDD)
- Ensure selected date has market data
- Check console logs for API responses

## Recent Updates (2025-01-21)

### Morning Session
1. Fixed substring matching bug that caused data misalignment
2. Added filtering to remove empty tenor rows
3. Improved historical data handling
4. Added comprehensive bid/ask spreads
5. Documented 1D/2D/3D ticker investigation results
6. Enhanced error handling and logging

### Afternoon Session - Historical Analysis Feature
1. Added new Historical Analysis tab with time series table
2. Implemented date range selector (7 days to 2 years)
3. Added tenor-specific historical view
4. Created tab navigation between Surface and Historical views
5. Maintained consistent GZC Intel app styling
6. Optimized historical data fetching with parallel API calls

## References

- [Bloomberg Ticker Reference](./bloomberg-api-vm-documentation/BLOOMBERG_TICKER_REFERENCE.md)
- [Short-dated Ticker Investigation](./bloomberg-api-vm-documentation/SHORT_DATED_TICKER_INVESTIGATION.md)
- [Bloomberg Real-Time Volatilities Guide](https://data.bloomberglp.com/professional/sites/10/750114_Real-Time-Volatilities.pdf)