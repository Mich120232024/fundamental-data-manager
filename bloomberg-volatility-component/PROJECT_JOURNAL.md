# Bloomberg Volatility Component - Project Journal

## 2025-01-21: Historical Volatility Table Feature

### Feature Added
- **New Component**: `VolatilityHistoricalTable` - displays historical volatility data in table format
- **Tab Navigation**: Added tabs to switch between Surface view and Historical Analysis view
- **Date Range Selection**: Supports 7 days to 2 years of historical data
- **Tenor Selection**: Choose specific tenor (ON, 1W, 2W, etc.) for focused analysis
- **Currency Pair Selection**: All 28 major FX pairs supported

### Implementation Details
1. Created `MainAppContainer.tsx` to handle tab navigation
2. Historical table shows:
   - Date column (most recent first)
   - ATM volatility
   - Risk Reversals for all deltas (5D, 10D, 15D, 25D, 35D)
   - Butterflies for all deltas
3. Fetches data using existing Bloomberg historical endpoint
4. Consistent styling with GZC Intel app design language

### Technical Decisions
- Table-based display (no charts) for consistency with existing surface view
- Sticky headers for better usability with long data sets
- Color coding for risk reversals (green/red for positive/negative)
- Efficient data fetching with Promise.all for parallel API calls

### API Usage
- Endpoint: `/api/bloomberg/historical`
- Fields: `PX_LAST` (sufficient for historical analysis)
- Date format: YYYYMMDD

### Files Created/Modified
- `src/components/VolatilityHistoricalTable.tsx` (new)
- `src/components/MainAppContainer.tsx` (new)
- `src/App.tsx` (modified to use MainAppContainer)

### Next Steps
- Could add export functionality for historical data
- Could add statistical analysis (mean, std dev, etc.)
- Could add comparison between different tenors

### Files Documentation
- Created comprehensive HISTORICAL_ANALYSIS_FEATURE.md
- Updated README.md with new feature details
- Updated CLAUDE.md with recent context
- Maintained PROJECT_JOURNAL.md

---

## 2025-01-20: Major Debugging Session

### Issues Resolved
1. **Wrong API Running**: Fixed by identifying correct script (`main_checkpoint_working_2025_07_16.py`)
2. **Substring Matching Bug**: Fixed data misalignment where 35D showed in 5D column
3. **Empty Tenor Rows**: Added filtering to remove rows with no data
4. **1D/2D/3D Investigation**: Confirmed these tickers don't exist in Bloomberg FX options

### Key Learnings
- Always use regex for ticker parsing, never substring matching
- Test API endpoints with curl before debugging React
- Bloomberg ticker formats vary by data subscription
- Document everything for future reference

---

## 2025-01-16: Initial Bloomberg API Integration

### Checkpoint Created
- Working Bloomberg API on Azure VM
- Real-time volatility surface data
- Support for all major FX pairs
- Full delta coverage (5D through 35D)

### Architecture
- React + TypeScript frontend
- FastAPI Python backend on Windows VM
- Bloomberg Terminal integration via blpapi
- Azure hosting with NSG security

### Documentation
- Comprehensive README created
- API troubleshooting guide
- Bloomberg ticker reference
- Lessons learned document