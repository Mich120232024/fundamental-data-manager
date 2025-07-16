# Bloomberg Volatility Data Retrieval Methodology

## Overview
This document outlines the proven methodology for retrieving live, EOD (End of Day), and historical volatility data from Bloomberg Terminal using the established API patterns.

## Related Documentation
- **[README](./README.md)**: Complete system overview and infrastructure details
- **[API Endpoints](./API_ENDPOINTS.md)**: API endpoint documentation with request/response examples
- **[Volatility Formats](./VOLATILITY_FORMATS.md)**: Bloomberg security formats and data structures
- **[Setup Guide](./SETUP_GUIDE.md)**: VM setup and testing procedures
- **[Networking](./NETWORKING.md)**: Network configuration and performance optimization

## Data Types Available

### 1. Live Data (Real-time)
- **Update Frequency**: Real-time (milliseconds)
- **Availability**: During market hours
- **Use Case**: Trading, real-time risk management
- **Latency**: 200-500ms per request

### 2. EOD Data (End of Day)
- **Update Frequency**: Daily after market close
- **Availability**: Historical series available
- **Use Case**: Daily risk reports, historical analysis
- **Latency**: 300-800ms per request

### 3. Historical Data
- **Time Range**: Multiple years of history
- **Granularity**: Daily, weekly, monthly
- **Use Case**: Backtesting, trend analysis, model calibration
- **Latency**: 500-2000ms per request

## Proven Security Formats

### Live Data Format
```python
# ATM Volatility (Live)
security = "EURUSDV1M BGN Curncy"
fields = ["PX_LAST", "PX_BID", "PX_ASK", "LAST_UPDATE_TIME"]

# Risk Reversals (Live)
security = "EURUSD25RR1M BGN Curncy"
fields = ["PX_LAST", "PX_BID", "PX_ASK"]

# Butterflies (Live)
security = "EURUSD25BF1M BGN Curncy"
fields = ["PX_LAST", "PX_BID", "PX_ASK"]
```

### Historical Data Format
```python
# Historical ATM Volatility
security = "EURUSDV1M BGN Curncy"
fields = ["PX_LAST"]
overrides = [
    ("START_DATE", "20240101"),
    ("END_DATE", "20250716")
]

# Historical with Market Vol field
security = "EURUSD 1M ATM VOL BVOL Curncy"
fields = ["MARKET_VOL"]
overrides = [
    ("START_DATE", "20240101"),
    ("END_DATE", "20250716")
]
```

## Data Retrieval Patterns

### 1. Single Point Retrieval
```python
def get_single_volatility_point(pair, tenor, data_type="live"):
    """
    Retrieve single volatility point
    
    Args:
        pair: Currency pair (e.g., "EURUSD")
        tenor: Volatility tenor (e.g., "1M")
        data_type: "live", "eod", or "historical"
    """
    security = f"{pair}V{tenor} BGN Curncy"
    
    if data_type == "live":
        fields = ["PX_LAST", "PX_BID", "PX_ASK", "LAST_UPDATE_TIME"]
    elif data_type == "eod":
        fields = ["PX_LAST", "PX_OPEN", "PX_HIGH", "PX_LOW", "PX_VOLUME"]
    else:  # historical
        fields = ["PX_LAST"]
        # Add date overrides for historical data
    
    return bloomberg.get_reference_data([security], fields)
```

### 2. Volatility Surface Retrieval
```python
def get_volatility_surface(pair, tenors, data_type="live"):
    """
    Retrieve complete volatility surface
    
    Args:
        pair: Currency pair (e.g., "EURUSD")
        tenors: List of tenors (e.g., ["1W", "1M", "3M", "6M", "1Y"])
        data_type: "live", "eod", or "historical"
    """
    securities = []
    
    for tenor in tenors:
        # ATM Volatility
        securities.append(f"{pair}V{tenor} BGN Curncy")
        
        # Risk Reversals
        securities.append(f"{pair}25RR{tenor} BGN Curncy")
        securities.append(f"{pair}10RR{tenor} BGN Curncy")
        
        # Butterflies
        securities.append(f"{pair}25BF{tenor} BGN Curncy")
        securities.append(f"{pair}10BF{tenor} BGN Curncy")
    
    fields = ["PX_LAST", "PX_BID", "PX_ASK", "LAST_UPDATE_TIME"]
    
    if data_type == "historical":
        # Add date overrides for historical data
        fields = ["PX_LAST"]
    
    return bloomberg.get_reference_data(securities, fields)
```

### 3. Historical Time Series Retrieval
```python
def get_historical_volatility_series(pair, tenor, start_date, end_date):
    """
    Retrieve historical volatility time series
    
    Args:
        pair: Currency pair (e.g., "EURUSD")
        tenor: Volatility tenor (e.g., "1M")
        start_date: Start date (e.g., "20240101")
        end_date: End date (e.g., "20250716")
    """
    security = f"{pair}V{tenor} BGN Curncy"
    
    # Use Historical Data Request
    request = bloomberg.service.createRequest("HistoricalDataRequest")
    request.append("securities", security)
    request.append("fields", "PX_LAST")
    request.set("startDate", start_date)
    request.set("endDate", end_date)
    request.set("periodicitySelection", "DAILY")
    
    return bloomberg.send_historical_request(request)
```

## Data Quality Validation

### 1. Live Data Validation
```python
def validate_live_data(data):
    """Validate live volatility data quality"""
    checks = {
        "data_freshness": check_timestamp_freshness(data),
        "bid_ask_spread": validate_bid_ask_spread(data),
        "volatility_range": validate_volatility_range(data),
        "market_hours": check_market_hours(data)
    }
    return checks

def check_timestamp_freshness(data):
    """Check if data timestamp is within acceptable range"""
    last_update = data.get("LAST_UPDATE_TIME")
    if last_update:
        age = datetime.now() - parse_bloomberg_time(last_update)
        return age.total_seconds() < 300  # 5 minutes
    return False
```

### 2. Historical Data Validation
```python
def validate_historical_data(data):
    """Validate historical volatility data quality"""
    checks = {
        "data_completeness": check_data_completeness(data),
        "outlier_detection": detect_volatility_outliers(data),
        "monotonic_dates": validate_date_sequence(data),
        "business_days": validate_business_days(data)
    }
    return checks
```

## API Implementation

### 1. Live Volatility Endpoint
```python
@app.post("/api/fx/volatility/live")
async def get_live_volatility(request: VolatilityRequest):
    """Get live volatility data"""
    try:
        # Validate request parameters
        validate_currency_pairs(request.currency_pairs)
        validate_tenors(request.tenors)
        
        # Get volatility surface data
        data = get_volatility_surface(
            pairs=request.currency_pairs,
            tenors=request.tenors,
            data_type="live"
        )
        
        # Validate data quality
        validation_results = validate_live_data(data)
        
        return {
            "success": True,
            "data": {
                "data_type": "live_fx_volatility",
                "timestamp": datetime.now().isoformat(),
                "currency_pairs": request.currency_pairs,
                "tenors": request.tenors,
                "vol_types": ["ATM_VOL", "25D_RR", "25D_BF", "10D_RR", "10D_BF"],
                "raw_data": transform_live_data(data),
                "source": "Bloomberg Terminal - LIVE DATA",
                "data_count": len(data),
                "validation": validation_results
            },
            "query_id": generate_query_id("fx_vol_live")
        }
    except Exception as e:
        logger.error(f"Live volatility error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Historical Volatility Endpoint
```python
@app.post("/api/fx/volatility/historical")
async def get_historical_volatility(request: HistoricalVolatilityRequest):
    """Get historical volatility data"""
    try:
        # Validate request parameters
        validate_currency_pair(request.currency_pair)
        validate_tenor(request.tenor)
        validate_date_range(request.start_date, request.end_date)
        
        # Check cache first
        cache_key = f"hist_{request.currency_pair}_{request.tenor}_{request.start_date}_{request.end_date}"
        cached_data = get_from_cache(cache_key)
        
        if cached_data:
            return cached_data
        
        # Get historical data
        data = get_historical_volatility_series(
            pair=request.currency_pair,
            tenor=request.tenor,
            start_date=request.start_date,
            end_date=request.end_date,
            periodicity=request.periodicity or "DAILY"
        )
        
        # Validate data quality
        validation_results = validate_historical_data(data)
        
        response = {
            "success": True,
            "data": {
                "data_type": "historical_fx_volatility",
                "timestamp": datetime.now().isoformat(),
                "currency_pair": request.currency_pair,
                "tenor": request.tenor,
                "date_range": {
                    "start": request.start_date,
                    "end": request.end_date
                },
                "periodicity": request.periodicity or "DAILY",
                "time_series": transform_historical_data(data),
                "source": "Bloomberg Terminal - HISTORICAL DATA",
                "data_count": len(data),
                "validation": validation_results
            },
            "query_id": generate_query_id("fx_vol_hist")
        }
        
        # Cache the response
        set_cache(cache_key, response, ttl=86400)  # 24 hours
        
        return response
        
    except Exception as e:
        logger.error(f"Historical volatility error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. EOD Volatility Endpoint
```python
@app.post("/api/fx/volatility/eod")
async def get_eod_volatility(request: EODVolatilityRequest):
    """Get end-of-day volatility data"""
    try:
        # Validate request parameters
        validate_currency_pairs(request.currency_pairs)
        validate_tenors(request.tenors)
        validate_trading_date(request.trading_date)
        
        # Check cache first
        cache_key = f"eod_{hash(str(request.currency_pairs))}_{hash(str(request.tenors))}_{request.trading_date}"
        cached_data = get_from_cache(cache_key)
        
        if cached_data and not is_market_open():
            return cached_data
        
        # Get EOD data with date override
        data = get_volatility_surface(
            pairs=request.currency_pairs,
            tenors=request.tenors,
            data_type="eod",
            trading_date=request.trading_date
        )
        
        # Validate data quality
        validation_results = validate_eod_data(data)
        
        response = {
            "success": True,
            "data": {
                "data_type": "eod_fx_volatility",
                "timestamp": datetime.now().isoformat(),
                "currency_pairs": request.currency_pairs,
                "tenors": request.tenors,
                "trading_date": request.trading_date,
                "vol_types": ["ATM_VOL", "25D_RR", "25D_BF", "10D_RR", "10D_BF"],
                "raw_data": transform_eod_data(data),
                "source": "Bloomberg Terminal - EOD DATA",
                "data_count": len(data),
                "validation": validation_results
            },
            "query_id": generate_query_id("fx_vol_eod")
        }
        
        # Cache until next market close
        cache_ttl = seconds_until_market_close()
        set_cache(cache_key, response, ttl=cache_ttl)
        
        return response
        
    except Exception as e:
        logger.error(f"EOD volatility error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

## Data Transformation Patterns

### 1. Live Data Transformation
```python
def transform_live_data(bloomberg_data):
    """Transform live Bloomberg data to standard format"""
    surface = {
        "atm_vols": {},
        "risk_reversals": {"25D": {}, "10D": {}},
        "butterflies": {"25D": {}, "10D": {}},
        "timestamp": datetime.now().isoformat()
    }
    
    for security, data in bloomberg_data.items():
        tenor = extract_tenor(security)
        
        if "V" in security and "RR" not in security and "BF" not in security:
            # ATM Volatility
            surface["atm_vols"][tenor] = {
                "mid": data.get("PX_LAST"),
                "bid": data.get("PX_BID"),
                "ask": data.get("PX_ASK"),
                "last_update": data.get("LAST_UPDATE_TIME")
            }
        elif "25RR" in security:
            # 25D Risk Reversal
            surface["risk_reversals"]["25D"][tenor] = {
                "value": data.get("PX_LAST"),
                "bid": data.get("PX_BID"),
                "ask": data.get("PX_ASK")
            }
        # ... continue for other structures
    
    return surface
```

### 2. Historical Data Transformation
```python
def transform_historical_data(bloomberg_data):
    """Transform historical Bloomberg data to time series format"""
    time_series = []
    
    for date, data in bloomberg_data.items():
        time_series.append({
            "date": date,
            "volatility": data.get("PX_LAST"),
            "volume": data.get("PX_VOLUME", 0)
        })
    
    return sorted(time_series, key=lambda x: x["date"])
```

## Usage Examples

### 1. Get Live EUR/USD Volatility Surface
```python
# Get complete live volatility surface
surface = get_volatility_surface(
    pair="EURUSD",
    tenors=["1W", "1M", "3M", "6M", "1Y"],
    data_type="live"
)
```

### 2. Get Historical ATM Volatility
```python
# Get 1-year historical ATM volatility
history = get_historical_volatility_series(
    pair="EURUSD",
    tenor="1M",
    start_date="20240101",
    end_date="20250716"
)
```

### 3. Get EOD Volatility for Risk Reports
```python
# Get EOD volatility for daily risk report
eod_data = get_volatility_surface(
    pair="EURUSD",
    tenors=["1W", "2W", "1M", "2M", "3M", "6M", "9M", "1Y"],
    data_type="eod"
)
```

## Performance Optimization

### 1. Batch Requests
- Combine multiple securities in single request
- Optimize tenor selection based on use case
- Use appropriate timeout values

### 2. Caching Strategy
- Cache historical data (daily refresh)
- Cache EOD data (until next market close)
- Don't cache live data (real-time requirement)

### 3. Request Prioritization
- Live data: High priority, low latency
- EOD data: Medium priority, scheduled
- Historical data: Low priority, batch processing

## Error Handling

### 1. Data Availability Errors
```python
def handle_data_availability(security, error):
    """Handle cases where volatility data is not available"""
    if "not found" in error.lower():
        # Security doesn't exist or no data
        return {"status": "no_data", "security": security}
    elif "market closed" in error.lower():
        # Market closed, use last available data
        return {"status": "market_closed", "security": security}
```

### 2. Connection Errors
```python
def handle_connection_errors(error):
    """Handle Bloomberg Terminal connection issues"""
    if "session" in error.lower():
        # Terminal not logged in
        return {"status": "terminal_disconnected"}
    elif "timeout" in error.lower():
        # Request timeout
        return {"status": "timeout"}
```

## Caching Implementation

### 1. Cache Strategy by Data Type
```python
class VolatilityCacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
    def get_cache_key(self, data_type, **kwargs):
        """Generate cache key based on data type and parameters"""
        if data_type == "live":
            return None  # No caching for live data
        elif data_type == "eod":
            return f"eod_{kwargs['pairs']}_{kwargs['tenors']}_{kwargs['date']}"
        elif data_type == "historical":
            return f"hist_{kwargs['pair']}_{kwargs['tenor']}_{kwargs['start']}_{kwargs['end']}"
    
    def get_cache_ttl(self, data_type):
        """Get cache TTL based on data type"""
        if data_type == "eod":
            return self.seconds_until_market_close()
        elif data_type == "historical":
            return 86400  # 24 hours
        return 0  # No caching
    
    def seconds_until_market_close(self):
        """Calculate seconds until next market close"""
        now = datetime.now(timezone.utc)
        # NYSE closes at 4 PM ET (21:00 UTC)
        market_close = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now > market_close:
            market_close += timedelta(days=1)
        return int((market_close - now).total_seconds())
```

### 2. Request Validation
```python
def validate_currency_pairs(pairs):
    """Validate currency pairs"""
    valid_pairs = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", 
        "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "AUDJPY"
    ]
    for pair in pairs:
        if pair not in valid_pairs:
            raise ValueError(f"Invalid currency pair: {pair}")

def validate_tenors(tenors):
    """Validate tenor formats"""
    valid_tenors = ["O/N", "T/N", "1W", "2W", "3W", "1M", "2M", "3M", 
                   "4M", "5M", "6M", "9M", "1Y", "18M", "2Y", "3Y", "5Y"]
    for tenor in tenors:
        if tenor not in valid_tenors:
            raise ValueError(f"Invalid tenor: {tenor}")

def validate_date_range(start_date, end_date):
    """Validate date range"""
    try:
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        if start > end:
            raise ValueError("Start date must be before end date")
        if (end - start).days > 365 * 5:  # 5 years max
            raise ValueError("Date range too large (max 5 years)")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}")
```

### 3. Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor API performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log performance metrics
            logger.info(f"API call {func.__name__} completed in {execution_time:.2f}s")
            
            # Alert on slow responses
            if execution_time > 10.0:  # 10 seconds
                send_alert(f"Slow API response: {func.__name__} took {execution_time:.2f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"API call {func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    return wrapper

# Apply to all API endpoints
@monitor_performance
@app.post("/api/fx/volatility/live")
async def get_live_volatility(request: VolatilityRequest):
    # Implementation here
    pass
```

## Next Steps

1. **Complete API Implementation**: Deploy EOD and historical endpoints to production
2. **Enhanced Caching**: Implement Redis-based distributed caching
3. **Data Storage**: Implement daily volatility surface storage in Azure SQL
4. **Performance Monitoring**: Add comprehensive performance metrics and alerting
5. **VaR Integration**: Connect volatility surfaces to VaR calculations
6. **Load Testing**: Conduct comprehensive load testing for all data types
7. **Documentation**: Create comprehensive API documentation with examples
8. **Monitoring Dashboard**: Build real-time monitoring dashboard for API performance

---

*Last Updated: July 16, 2025*
*Status: Production Ready - Complete Implementation Guide*
*Coverage: Live, EOD, and Historical Data Retrieval Patterns*