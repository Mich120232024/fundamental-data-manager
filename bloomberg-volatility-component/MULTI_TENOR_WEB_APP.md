# Bloomberg-Style Multi-Tenor Volatility Surface Web Application

## Overview

We've created a web application that displays FX option volatility surfaces in a Bloomberg Terminal-style interface. The application fetches real-time data from the Bloomberg API and presents it in a familiar format with all available deltas.

## Features

### 1. Multi-Tenor Support
- Supports all standard FX option tenors from 1D to 2Y
- Tested tenors: 1W, 2W, 1M, 2M, 3M, 6M, 1Y
- Full list available: 1D, 1W, 2W, 3W, 1M, 2M, 3M, 4M, 5M, 6M, 9M, 1Y, 15M, 18M, 2Y

### 2. All Available Deltas
- Displays all Bloomberg-supported deltas: 5D, 10D, 15D, 25D, 35D
- Shows both Risk Reversals (RR) and Butterflies (BF)
- ATM volatility with bid/ask spreads

### 3. Bloomberg Terminal Styling
- Black background with amber/orange headers
- Color-coded values (green for positive, red for negative)
- Hover effects for better readability
- Monospace font for data alignment

### 4. Interactive Features
- Currency pair selection (EURUSD, USDJPY, GBPUSD, USDCHF)
- Toggle between Bid/Ask and Mid/Spread views
- Format selection (RR/BF or Put/Call)
- Real-time data refresh

## Sample Output

```
====================================================================================================
Bloomberg-Style Volatility Matrix (10D and 25D only)
====================================================================================================
Exp  ATM_Bid  ATM_Ask  ATM_Mid  25D_RR  25D_BF  10D_RR  10D_BF
 1W    7.570    8.980    8.275   0.147   0.185   0.320   0.627
 2W    7.595    8.605    8.100   0.250   0.188   0.468   0.620
 1M    7.965    8.405    8.185   0.200   0.170   0.312   0.620
 2M    7.685    8.060    7.872   0.240   0.177   0.405   0.647
 3M    7.640    7.940    7.790   0.270   0.185   0.480   0.675
 6M    7.495    7.745    7.620   0.352   0.207   0.630   0.750
 1Y    7.450    7.700    7.575   0.443   0.242   0.800   0.890
```

## Architecture

### Backend Components

1. **MultiTenorVolatilityClient** (`src/api/multi_tenor_client.py`)
   - Fetches data for multiple tenors in parallel
   - Creates Bloomberg-style and full delta matrices
   - Handles error cases gracefully

2. **Web Application** (`web_app.py`)
   - FastAPI-based REST API
   - Endpoints:
     - `GET /` - Main web interface
     - `GET /api/volatility/{currency_pair}` - Multi-tenor data
     - `GET /api/volatility/{currency_pair}/{tenor}` - Single tenor details

3. **Frontend** (`templates/index.html`)
   - Pure JavaScript (no frameworks)
   - Bloomberg Terminal-inspired styling
   - Real-time data updates

### Data Flow

```
Bloomberg Terminal (VM)
        ↓
Bloomberg API (http://20.172.249.92:8080)
        ↓
MultiTenorVolatilityClient
        ↓
FastAPI Web Server
        ↓
Browser Interface
```

## Running the Application

### Option 1: Using the startup script
```bash
cd local_engine
./start_web_app.sh
```

### Option 2: Manual startup
```bash
cd local_engine
pip3 install -r requirements.txt
python3 web_app.py
```

Then open http://localhost:8000 in your browser.

## API Endpoints

### Get Multi-Tenor Surface
```
GET /api/volatility/EURUSD
```

Response:
```json
{
  "currency_pair": "EURUSD",
  "bloomberg_style": [...],  // 10D and 25D data only
  "full_delta": [...],       // All deltas (5D, 10D, 15D, 25D, 35D)
  "success_count": 7,
  "failed_count": 0
}
```

### Get Single Tenor Details
```
GET /api/volatility/EURUSD/1M
```

## Next Steps

1. **3D Surface Visualization**
   - Implement interactive 3D volatility surface using Plotly
   - Show volatility smile across strikes and tenors

2. **Historical Analysis**
   - Add date picker for historical data
   - Show volatility term structure evolution

3. **Additional Features**
   - Export to Excel functionality
   - Real-time auto-refresh
   - More currency pairs
   - Greeks calculation

4. **Performance Optimization**
   - Cache frequently requested data
   - WebSocket for real-time updates
   - Batch API requests

## Technical Notes

- The application fetches data in parallel for better performance
- Failed tenor requests are handled gracefully without blocking others
- All data comes from real Bloomberg Terminal - no mock data
- Spread is calculated as Ask - Bid for all values