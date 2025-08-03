#!/usr/bin/env python3
"""
Bloomberg Gateway API - Production-Ready Service
Designed for containerized deployment (Kubernetes/Azure Container Apps)

Environment Variables:
- BLOOMBERG_API_URL: Bloomberg VM endpoint (default: http://20.172.249.92:8080)
- REDIS_CONNECTION: Redis connection string (optional, for production)
- ENABLE_CACHE: Enable caching (default: false for dev, true for prod)
- CACHE_TTL: Cache time-to-live in seconds (default: 900)
- LOG_LEVEL: Logging level (default: INFO)
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio
from contextlib import asynccontextmanager

# Import yield curve router - DISABLED
# from yield_curve_db_endpoint import yield_curve_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
BLOOMBERG_API_URL = os.getenv("BLOOMBERG_API_URL", "http://20.172.249.92:8080")
REDIS_CONNECTION = os.getenv("REDIS_CONNECTION")
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "false").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "900"))  # 15 minutes default

# Load ticker repository
TICKER_REPO_PATH = Path(__file__).parent.parent / "knowledge" / "technical_resources" / "bloomberg_api" / "central_bloomberg_ticker_repository_v3.json"
if not TICKER_REPO_PATH.exists():
    # Fallback for local development
    TICKER_REPO_PATH = Path(__file__).parent / "central_bloomberg_ticker_repository_v3.json"

try:
    with open(TICKER_REPO_PATH) as f:
        TICKER_REPOSITORY = json.load(f)
    logger.info(f"Loaded {TICKER_REPOSITORY['metadata']['total_valid_tickers']} tickers from repository")
except Exception as e:
    logger.warning(f"Could not load ticker repository: {e}")
    TICKER_REPOSITORY = None

# Cache implementation
class CacheManager:
    def __init__(self):
        self.cache = {}
        self.redis_client = None
        
        if REDIS_CONNECTION and ENABLE_CACHE:
            try:
                import redis
                self.redis_client = redis.from_url(REDIS_CONNECTION)
                self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
    
    async def get(self, key: str) -> Optional[Dict]:
        if not ENABLE_CACHE:
            return None
            
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        else:
            # In-memory cache
            if key in self.cache:
                data, timestamp = self.cache[key]
                if datetime.now() - timestamp < timedelta(seconds=CACHE_TTL):
                    return data
                else:
                    del self.cache[key]
        return None
    
    async def set(self, key: str, value: Dict):
        if not ENABLE_CACHE:
            return
            
        if self.redis_client:
            try:
                self.redis_client.setex(key, CACHE_TTL, json.dumps(value))
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        else:
            # In-memory cache
            self.cache[key] = (value, datetime.now())
    
    async def clear(self):
        if self.redis_client:
            self.redis_client.flushdb()
        else:
            self.cache.clear()

# Initialize cache
cache_manager = CacheManager()

# HTTP client
http_client = httpx.AsyncClient(timeout=30.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Bloomberg Gateway starting up...")
    logger.info(f"Cache enabled: {ENABLE_CACHE}")
    logger.info(f"Bloomberg API: {BLOOMBERG_API_URL}")
    yield
    # Shutdown
    await http_client.aclose()
    logger.info("Bloomberg Gateway shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Bloomberg Gateway API",
    version="3.0.0",
    description="Production-ready Bloomberg data gateway with intelligent ticker selection",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - DISABLED
# app.include_router(yield_curve_router)

# Models
class VolatilityRequest(BaseModel):
    pair: str
    tenors: Optional[List[str]] = None  # If not provided, use standard tenors

class VolatilityResponse(BaseModel):
    data: Dict[str, Any]
    metadata: Dict[str, Any]

# Helper functions
def get_volatility_tickers(pair: str, tenors: List[str]) -> Dict[str, List[str]]:
    """Get the best available tickers for a currency pair"""
    tickers = {
        "spot": [f"{pair} Curncy"],
        "atm": [],
        "rr_25d": [],
        "bf_25d": [],
        "forwards": []
    }
    
    for tenor in tenors:
        if tenor == "ON":
            tickers["atm"].append(f"{pair}VON Curncy")
        else:
            tickers["atm"].append(f"{pair}V{tenor} BGN Curncy")
            tickers["atm"].append(f"{pair}V{tenor} Curncy")  # Fallback
        
        # Risk reversal and butterfly
        tickers["rr_25d"].append(f"{pair}25R{tenor} BGN Curncy")
        tickers["rr_25d"].append(f"{pair}25R{tenor} Curncy")  # Fallback
        tickers["bf_25d"].append(f"{pair}25B{tenor} BGN Curncy")
        tickers["bf_25d"].append(f"{pair}25B{tenor} Curncy")  # Fallback
        
        # Forwards
        tickers["forwards"].append(f"{pair}{tenor} Curncy")
    
    return tickers

async def fetch_bloomberg_data(securities: List[str], fields: List[str]) -> Dict:
    """Fetch data from Bloomberg API"""
    payload = {
        "securities": securities,
        "fields": fields
    }
    
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    try:
        response = await http_client.post(
            f"{BLOOMBERG_API_URL}/api/bloomberg/reference",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Bloomberg API error: {response.status_code}")
            return {"error": f"Bloomberg API returned {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Bloomberg API connection error: {e}")
        return {"error": str(e)}

# API Endpoints
@app.get("/")
async def root():
    return {
        "name": "Bloomberg Gateway API",
        "version": "3.0.0",
        "status": "ready",
        "cache_enabled": ENABLE_CACHE,
        "bloomberg_api": BLOOMBERG_API_URL,
        "ticker_repository": TICKER_REPOSITORY is not None,
        "environment": "development" if not ENABLE_CACHE else "production"
    }

@app.get("/health")
async def health_check():
    """Kubernetes/Container health check endpoint"""
    # Check Bloomberg API
    try:
        response = await http_client.get(f"{BLOOMBERG_API_URL}/health", timeout=5.0)
        bloomberg_status = response.status_code == 200
    except:
        bloomberg_status = False
    
    return {
        "status": "healthy" if bloomberg_status else "degraded",
        "bloomberg_api": bloomberg_status,
        "cache": ENABLE_CACHE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/volatility/{pair}", response_model=VolatilityResponse)
async def get_volatility_surface(pair: str, force_fresh: bool = False):
    """
    Get complete volatility surface for a currency pair
    Uses intelligent ticker selection from our 3,001 discovered tickers
    """
    cache_key = f"vol_{pair}"
    
    # Check cache first (unless forced fresh)
    if not force_fresh:
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            return VolatilityResponse(
                data=cached_data,
                metadata={
                    "source": "CACHE",
                    "cached_at": cached_data.get("timestamp"),
                    "pair": pair,
                    "cache_ttl": CACHE_TTL
                }
            )
    
    # Define standard tenors
    tenors = ["ON", "1W", "2W", "1M", "2M", "3M", "6M", "9M", "1Y", "18M", "2Y"]
    
    # Get tickers
    ticker_groups = get_volatility_tickers(pair, tenors)
    all_tickers = []
    for group in ticker_groups.values():
        all_tickers.extend(group)
    
    # Fetch from Bloomberg
    fields = ["PX_LAST", "PX_BID", "PX_ASK", "LAST_UPDATE"]
    bloomberg_response = await fetch_bloomberg_data(all_tickers, fields)
    
    if "error" in bloomberg_response:
        raise HTTPException(status_code=503, detail=bloomberg_response["error"])
    
    # Process response
    processed_data = {
        "pair": pair,
        "timestamp": datetime.now().isoformat(),
        "tenors": {},
        "spot": None
    }
    
    # Extract data
    if "data" in bloomberg_response and "securities_data" in bloomberg_response["data"]:
        for security_data in bloomberg_response["data"]["securities_data"]:
            if security_data.get("success"):
                ticker = security_data["security"]
                fields = security_data.get("fields", {})
                
                # Process based on ticker type
                if ticker == f"{pair} Curncy":
                    processed_data["spot"] = fields.get("PX_LAST")
                # Add more processing logic here
    
    # Cache the result
    await cache_manager.set(cache_key, processed_data)
    
    return VolatilityResponse(
        data=processed_data,
        metadata={
            "source": "BLOOMBERG_LIVE",
            "fetched_at": datetime.now().isoformat(),
            "pair": pair,
            "tickers_checked": len(all_tickers)
        }
    )

@app.post("/api/cache/clear")
async def clear_cache():
    """Clear cache - useful for development"""
    if ENABLE_CACHE:
        await cache_manager.clear()
        return {"status": "Cache cleared"}
    else:
        return {"status": "Cache not enabled"}

# Direct proxy endpoints for frontend compatibility
@app.post("/api/bloomberg/reference")
async def bloomberg_reference_proxy(request: Dict[str, Any]):
    """Direct proxy to Bloomberg reference endpoint - for frontend compatibility"""
    try:
        payload = {
            "securities": request.get("securities", []),
            "fields": request.get("fields", [])
        }
        
        headers = {
            "Authorization": "Bearer test",
            "Content-Type": "application/json"
        }
        
        response = await http_client.post(
            f"{BLOOMBERG_API_URL}/api/bloomberg/reference",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Bloomberg API returned {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Bloomberg reference proxy error: {e}")
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/api/bloomberg/historical")
async def bloomberg_historical_proxy(request: Dict[str, Any]):
    """Direct proxy to Bloomberg historical endpoint - for frontend compatibility"""
    try:
        headers = {
            "Authorization": "Bearer test",
            "Content-Type": "application/json"
        }
        
        response = await http_client.post(
            f"{BLOOMBERG_API_URL}/api/bloomberg/historical",
            json=request,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Bloomberg API returned {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Bloomberg historical proxy error: {e}")
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/api/bloomberg/ticker-discovery")
async def bloomberg_ticker_discovery_proxy(request: Dict[str, Any]):
    """Proxy to VM ticker discovery endpoint"""
    try:
        headers = {
            "Authorization": "Bearer test",
            "Content-Type": "application/json"
        }
        
        response = await http_client.post(
            f"{BLOOMBERG_API_URL}/api/bloomberg/ticker-discovery",
            json=request,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Bloomberg API returned {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Ticker discovery proxy error: {e}")
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/api/bloomberg/validate-tickers")
async def bloomberg_validate_tickers_proxy(tickers: List[str]):
    """Proxy to VM ticker validation endpoint"""
    try:
        headers = {
            "Authorization": "Bearer test",
            "Content-Type": "application/json"
        }
        
        response = await http_client.post(
            f"{BLOOMBERG_API_URL}/api/bloomberg/validate-tickers",
            json=tickers,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Bloomberg API returned {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Ticker validation proxy error: {e}")
        raise HTTPException(status_code=503, detail=str(e))

# Trade Synchronization Endpoints
@app.post("/api/trades/sync-check")
async def check_trade_sync():
    """Check if database synchronization is needed"""
    import subprocess
    import os
    
    try:
        # Set PostgreSQL password from environment
        env = os.environ.copy()
        if 'POSTGRES_PASSWORD' not in env:
            logger.info("Getting PostgreSQL password from Azure Key Vault...")
            try:
                import subprocess
                password = subprocess.run([
                    'az', 'keyvault', 'secret', 'show', 
                    '--vault-name', 'gzc-finma-keyvault',
                    '--name', 'postgres-connection-string',
                    '--query', 'value', 
                    '-o', 'tsv'
                ], capture_output=True, text=True, timeout=10)
                
                if password.returncode == 0:
                    # Extract password from connection string: postgresql+asyncpg://mikael:PASSWORD@host...
                    connection_string = password.stdout.strip()
                    if '://' in connection_string and '@' in connection_string:
                        # Extract password between : and @
                        password_part = connection_string.split('://')[1].split('@')[0]
                        if ':' in password_part:
                            env['POSTGRES_PASSWORD'] = password_part.split(':')[1]
                            logger.info("✅ PostgreSQL password retrieved from Key Vault")
                        else:
                            raise ValueError("Cannot parse password from connection string")
                    else:
                        raise ValueError("Invalid connection string format")
                else:
                    raise subprocess.CalledProcessError(password.returncode, password.stderr)
                    
            except Exception as e:
                logger.error(f"❌ Failed to get password from Key Vault: {e}")
                raise ValueError("Cannot retrieve PostgreSQL password from Key Vault")
        
        # Run sync check script
        result = subprocess.run([
            'python3', 
            '/Users/mikaeleage/GZC Intel Workspace/scripts/database_analysis/check_and_sync_trades.py'
        ], 
        capture_output=True, 
        text=True, 
        env=env,
        timeout=30
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            logger.error(f"Sync check failed: {result.stderr}")
            return {"status": "error", "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Sync check timed out"}
    except Exception as e:
        logger.error(f"Sync check error: {e}")
        return {"status": "error", "error": str(e)}

@app.post("/api/trades/perform-sync")
async def perform_trade_sync():
    """Actually perform the trade synchronization"""
    import subprocess
    import os
    
    try:
        # Set PostgreSQL password from environment
        env = os.environ.copy()
        if 'POSTGRES_PASSWORD' not in env:
            logger.info("Getting PostgreSQL password from Azure Key Vault...")
            try:
                import subprocess
                password = subprocess.run([
                    'az', 'keyvault', 'secret', 'show', 
                    '--vault-name', 'gzc-finma-keyvault',
                    '--name', 'postgres-connection-string',
                    '--query', 'value', 
                    '-o', 'tsv'
                ], capture_output=True, text=True, timeout=10)
                
                if password.returncode == 0:
                    # Extract password from connection string: postgresql+asyncpg://mikael:PASSWORD@host...
                    connection_string = password.stdout.strip()
                    if '://' in connection_string and '@' in connection_string:
                        # Extract password between : and @
                        password_part = connection_string.split('://')[1].split('@')[0]
                        if ':' in password_part:
                            env['POSTGRES_PASSWORD'] = password_part.split(':')[1]
                            logger.info("✅ PostgreSQL password retrieved from Key Vault")
                        else:
                            raise ValueError("Cannot parse password from connection string")
                    else:
                        raise ValueError("Invalid connection string format")
                else:
                    raise subprocess.CalledProcessError(password.returncode, password.stderr)
                    
            except Exception as e:
                logger.error(f"❌ Failed to get password from Key Vault: {e}")
                raise ValueError("Cannot retrieve PostgreSQL password from Key Vault")
        
        # Run sync with --sync flag
        result = subprocess.run([
            'python3', 
            '/Users/mikaeleage/GZC Intel Workspace/scripts/database_analysis/check_and_sync_trades.py',
            '--sync'
        ], 
        capture_output=True, 
        text=True, 
        env=env,
        timeout=120  # Longer timeout for actual sync
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            logger.error(f"Trade sync failed: {result.stderr}")
            return {"status": "error", "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Trade sync timed out"}
    except Exception as e:
        logger.error(f"Trade sync error: {e}")
        return {"status": "error", "error": str(e)}

@app.post("/api/option/price")
async def price_option(request: dict):
    """
    Price FX option using Garman-Kohlhagen model
    
    Expected request format:
    {
        "currency_pair": "USDMXN",
        "strike": 19.75,
        "time_to_expiry": 0.1389,  // in years
        "option_type": "call",     // "call" or "put"
        "notional": 10000000
    }
    """
    try:
        # Validate required fields
        required_fields = ['currency_pair', 'strike', 'time_to_expiry', 'option_type', 'notional']
        for field in required_fields:
            if field not in request:
                return {"status": "error", "error": f"Missing required field: {field}"}
        
        currency_pair = request['currency_pair']
        strike = float(request['strike'])
        time_to_expiry = float(request['time_to_expiry'])
        option_type = request['option_type'].lower()
        notional = float(request['notional'])
        price_date = request.get('price_date')  # Optional: YYYY-MM-DD format
        spot_override = request.get('spot_override')  # Optional: override spot rate
        
        # Validate option type
        if option_type not in ['call', 'put']:
            return {"status": "error", "error": "option_type must be 'call' or 'put'"}
        
        # Fetch required market data
        spot_ticker = f"{currency_pair} Curncy"
        
        # Determine which tenors to fetch for interpolation
        time_to_expiry_days = time_to_expiry * 365.25
        
        # Get volatility smile data for interpolation
        vol_tickers = []
        if time_to_expiry_days <= 30:
            # Use ON and 1M
            vol_tickers = [
                f"{currency_pair}VON Curncy",
                f"{currency_pair}V1M BGN Curncy",
                f"{currency_pair}25R1M BGN Curncy",
                f"{currency_pair}25B1M BGN Curncy"
            ]
        elif time_to_expiry_days <= 60:
            # Use 1M and 2M
            vol_tickers = [
                f"{currency_pair}V1M BGN Curncy",
                f"{currency_pair}25R1M BGN Curncy",
                f"{currency_pair}25B1M BGN Curncy",
                f"{currency_pair}V2M BGN Curncy",
                f"{currency_pair}25R2M BGN Curncy",
                f"{currency_pair}25B2M BGN Curncy"
            ]
        else:
            # Use 2M and 3M
            vol_tickers = [
                f"{currency_pair}V2M BGN Curncy",
                f"{currency_pair}25R2M BGN Curncy",
                f"{currency_pair}25B2M BGN Curncy",
                f"{currency_pair}V3M BGN Curncy",
                f"{currency_pair}25R3M BGN Curncy",
                f"{currency_pair}25B3M BGN Curncy"
            ]
        
        # Get currency-specific interest rate tickers
        base_currency = currency_pair[:3]
        quote_currency = currency_pair[3:]
        
        # Use validated ticker repository instead of hardcoded mappings
        def get_currency_rate_ticker(currency: str) -> str:
            """Get validated 1M rate ticker from repository"""
            if not TICKER_REPOSITORY:
                return None
                
            yield_curves = TICKER_REPOSITORY.get('yield_curve_construction', {})
            
            # Direct currency mapping - check main section first
            if currency in yield_curves:
                money_market = yield_curves[currency].get('money_market', {})
                term_rates = money_market.get('term', [])
                # Find 1M ticker (US0001M, EUR001M, etc.)
                for ticker in term_rates:
                    if '001M' in ticker or '0001M' in ticker:
                        return ticker
            
            # Check emerging markets section
            emerging = yield_curves.get('emerging_markets', {})
            if currency in emerging:
                money_market = emerging[currency].get('money_market', {})
                term_rates = money_market.get('term', []) if isinstance(money_market, dict) else money_market
                # Find 1M ticker
                for ticker in term_rates:
                    if isinstance(ticker, str) and ('1M' in ticker or '001M' in ticker):
                        return ticker
            
            # Special cases from validated testing
            if currency == 'MXN':
                return 'MXIBTIIE Index'  # Mexican interbank rate (tested working)
            
            return None
        
        # NO FALLBACKS - Only validated tickers from repository
        base_rate_ticker = get_currency_rate_ticker(base_currency)
        quote_rate_ticker = get_currency_rate_ticker(quote_currency)
        
        # Get supported currencies from repository
        supported_currencies = list(TICKER_REPOSITORY.get('yield_curve_construction', {}).keys()) + ['MXN']
        
        # Fail fast if currency not supported
        if not base_rate_ticker:
            return {"status": "error", "error": f"Unsupported base currency: {base_currency}. Only {supported_currencies} have validated rate tickers."}
        if not quote_rate_ticker:
            return {"status": "error", "error": f"Unsupported quote currency: {quote_currency}. Only {supported_currencies} have validated rate tickers."}
        
        # Fetch all market data in parallel
        securities = [spot_ticker] + vol_tickers + [base_rate_ticker, quote_rate_ticker]
        
        # Use historical data if price_date is provided
        if price_date:
            # Convert YYYY-MM-DD to YYYYMMDD for Bloomberg
            bbg_date = price_date.replace('-', '')
            # Fetch historical data for each security individually
            historical_results = []
            for security in securities:
                result = await bloomberg_historical_proxy({
                    "security": security,
                    "fields": ["PX_LAST"],
                    "start_date": bbg_date,
                    "end_date": bbg_date
                })
                historical_results.append(result)
            
            # Combine results into expected format
            market_data = {
                'success': all(r.get('success', False) for r in historical_results),
                'data': {
                    'historical_data': historical_results
                }
            }
        else:
            market_data = await bloomberg_reference_proxy({
                "securities": securities,
                "fields": ["PX_LAST"]
            })
        
        if not market_data.get('success'):
            logger.error(f"Market data fetch failed: {market_data}")
            return {"status": "error", "error": "Failed to fetch market data"}
        
        # Extract market data from nested structure
        if price_date and 'data' in market_data and 'historical_data' in market_data['data']:
            # Historical data structure
            historical_data = market_data['data']['historical_data']
            spot = None
            vol_data = {}
            base_rate = None
            quote_rate = None
            
            # Parse historical data
            logger.info(f"Parsing historical data for {len(historical_data)} securities")
            logger.info(f"Securities requested: {securities}")
            missing_rates = []  # Track which rates are missing for fallback
            
            for i, result in enumerate(historical_data):
                if i >= len(securities):
                    logger.warning(f"Result index {i} exceeds securities list length {len(securities)}")
                    continue
                    
                security_name = securities[i]
                
                # Check if we have a successful response
                if 'success' in result and result['success'] and 'data' in result:
                    # Historical data has nested structure: result['data']['data'] contains array of date points
                    hist_data = result['data']
                    if 'data' in hist_data and hist_data['data'] and len(hist_data['data']) > 0:
                        # Get the first date's data
                        date_data = hist_data['data'][0]
                        if 'values' in date_data and len(date_data['values']) > 0:
                            value = date_data['values'][0]  # PX_LAST is the first value
                            logger.info(f"Historical data for {security_name}: {value}")
                        else:
                            value = None
                            logger.warning(f"No values in data point for {security_name} (index {i})")
                    else:
                        value = None
                        logger.warning(f"No data points for {security_name} (index {i})")
                else:
                    # Check the actual error structure
                    value = None
                    error_msg = result.get('error', 'Result not successful')
                    logger.warning(f"Failed to get data for {security_name} (index {i}): {error_msg}")
                
                # Assign values based on position
                if i == 0:  # Spot
                    spot = value
                elif i < len(vol_tickers) + 1:  # Volatility data
                    ticker_name = vol_tickers[i-1]
                    if value is not None:
                        vol_data[ticker_name] = value
                elif i == len(securities) - 2:  # Base rate
                    base_rate = value
                    if value is None:
                        missing_rates.append(('base_rate', base_currency, securities[i]))
                elif i == len(securities) - 1:  # Quote rate
                    quote_rate = value
                    if value is None:
                        missing_rates.append(('quote_rate', quote_currency, securities[i]))
            
            # If interest rates are missing (weekend/holiday), try to get the most recent available rate
            if missing_rates:
                logger.info(f"Missing rates on {price_date}, attempting to fetch most recent available rates")
                
                for rate_type, currency, security in missing_rates:
                    # Try to get data for the last 7 days to find the most recent rate
                    end_date = datetime.strptime(price_date, '%Y-%m-%d')
                    start_date = end_date - timedelta(days=7)
                    
                    try:
                        fallback_result = await bloomberg_historical_proxy({
                            "security": security,
                            "fields": ["PX_LAST"],
                            "start_date": start_date.strftime('%Y%m%d'),
                            "end_date": end_date.strftime('%Y%m%d')
                        })
                        
                        if fallback_result.get('success') and 'data' in fallback_result:
                            fallback_data = fallback_result['data']
                            if 'data' in fallback_data and fallback_data['data']:
                                # Get the most recent data point
                                data_points = fallback_data['data']
                                # Sort by date to ensure we get the most recent
                                data_points.sort(key=lambda x: x.get('date', ''), reverse=True)
                                
                                for dp in data_points:
                                    if 'PX_LAST' in dp:
                                        latest_value = dp['PX_LAST']
                                        latest_date = dp.get('date', 'unknown')
                                        logger.info(f"Using {currency} rate from {latest_date}: {latest_value}")
                                        
                                        if rate_type == 'base_rate':
                                            base_rate = latest_value
                                        else:  # quote_rate
                                            quote_rate = latest_value
                                        break
                                else:
                                    logger.warning(f"No recent data with PX_LAST found for {security}")
                            else:
                                logger.warning(f"No data points in fallback response for {security}")
                        else:
                            logger.warning(f"Failed to fetch recent data for {security}")
                    except Exception as e:
                        logger.error(f"Error fetching fallback rate for {security}: {str(e)}")
        else:
            # Reference data structure
            securities_data = market_data['data']['securities_data']
            spot = None
            vol_data = {}
            base_rate = None
            quote_rate = None
            
            # Parse spot
            if securities_data[0]['success'] and 'PX_LAST' in securities_data[0]['fields']:
                spot = securities_data[0]['fields']['PX_LAST']
        
        # Apply spot override if provided
        if spot_override is not None:
            spot = float(spot_override)
        
        # Parse remaining data only for reference (non-historical) data
        if not price_date:
            # Parse volatility data (only for reference data)
            vol_ticker_count = len(vol_tickers)
            for i in range(1, vol_ticker_count + 1):
                if i < len(securities_data) and securities_data[i]['success']:
                    ticker_name = vol_tickers[i-1]
                    vol_data[ticker_name] = securities_data[i]['fields'].get('PX_LAST')
            
            # Parse rates
            if vol_ticker_count + 1 < len(securities_data):
                if securities_data[vol_ticker_count + 1]['success']:
                    base_rate = securities_data[vol_ticker_count + 1]['fields'].get('PX_LAST')
                if securities_data[vol_ticker_count + 2]['success']:
                    quote_rate = securities_data[vol_ticker_count + 2]['fields'].get('PX_LAST')
        
        # Calculate interpolated volatility with smile adjustment
        import math
        
        # Calculate moneyness
        moneyness = math.log(strike / spot)
        
        # Interpolate volatility based on time and strike
        if time_to_expiry_days <= 30:
            # Simple case - use 1M directly for now
            volatility = vol_data.get(f"{currency_pair}V1M BGN Curncy")
        elif time_to_expiry_days <= 60:
            # Interpolate between 1M and 2M
            atm_1m = vol_data.get(f"{currency_pair}V1M BGN Curncy", 0)
            atm_2m = vol_data.get(f"{currency_pair}V2M BGN Curncy", 0)
            rr_1m = vol_data.get(f"{currency_pair}25R1M BGN Curncy", 0)
            rr_2m = vol_data.get(f"{currency_pair}25R2M BGN Curncy", 0)
            bf_1m = vol_data.get(f"{currency_pair}25B1M BGN Curncy", 0)
            bf_2m = vol_data.get(f"{currency_pair}25B2M BGN Curncy", 0)
            
            # Time interpolation weight
            weight = (time_to_expiry_days - 30) / 30
            
            # Interpolate smile parameters
            atm_vol = atm_1m + weight * (atm_2m - atm_1m)
            rr_25d = rr_1m + weight * (rr_2m - rr_1m)
            bf_25d = bf_1m + weight * (bf_2m - bf_1m)
            
            # Apply smile adjustment for moneyness
            # 25-delta strikes approximation
            vol_25d_call = atm_vol + bf_25d + rr_25d / 2
            vol_25d_put = atm_vol + bf_25d - rr_25d / 2
            
            # Simplified smile interpolation based on moneyness
            if option_type == 'call' and moneyness > 0:
                # OTM call - extrapolate from ATM to 25d call
                # Approximate 25-delta moneyness
                approx_25d_moneyness = 0.3 * atm_vol/100 * math.sqrt(time_to_expiry)
                if moneyness <= approx_25d_moneyness:
                    # Linear interpolation between ATM and 25d
                    volatility = atm_vol + (vol_25d_call - atm_vol) * (moneyness / approx_25d_moneyness)
                else:
                    # Extrapolate beyond 25d
                    slope = (vol_25d_call - atm_vol) / approx_25d_moneyness
                    volatility = atm_vol + slope * moneyness
            elif option_type == 'put' and moneyness < 0:
                # OTM put - extrapolate from ATM to 25d put
                approx_25d_moneyness = -0.3 * atm_vol/100 * math.sqrt(time_to_expiry)
                if moneyness >= approx_25d_moneyness:
                    # Linear interpolation between ATM and 25d
                    volatility = atm_vol + (vol_25d_put - atm_vol) * (moneyness / approx_25d_moneyness)
                else:
                    # Extrapolate beyond 25d
                    slope = (vol_25d_put - atm_vol) / approx_25d_moneyness
                    volatility = atm_vol + slope * moneyness
            else:
                # Near ATM
                volatility = atm_vol
        else:
            # Use 2M for now (should interpolate with 3M)
            volatility = vol_data.get(f"{currency_pair}V2M BGN Curncy")
        
        # Validate we have all required data
        missing_data = []
        if not spot: missing_data.append("spot rate")
        if not volatility: missing_data.append("volatility")
        if not base_rate: missing_data.append(f"{base_currency} rate")
        if not quote_rate: missing_data.append(f"{quote_currency} rate")
        
        if missing_data:
            logger.error(f"Missing market data for {currency_pair}: {missing_data}")
            logger.error(f"Spot: {spot}, Vol: {volatility}, Base rate: {base_rate}, Quote rate: {quote_rate}")
            logger.error(f"Vol data received: {vol_data}")
            return {
                "status": "error", 
                "error": f"Incomplete market data - missing: {', '.join(missing_data)}",
                "data": {
                    "spot": spot,
                    "volatility": volatility,
                    "base_rate": base_rate,
                    "quote_rate": quote_rate,
                    "missing": missing_data
                }
            }
        
        # Import and use Garman-Kohlhagen pricing (we need to add this)
        from garman_kohlhagen import price_fx_option
        
        pricing_result = price_fx_option(
            spot=spot,
            strike=strike,
            time_to_expiry=time_to_expiry,
            domestic_rate=quote_rate,
            foreign_rate=base_rate,
            volatility=volatility,
            option_type=option_type,
            notional=notional
        )
        
        return {
            "status": "success",
            "pricing": pricing_result,
            "market_data": {
                "spot": spot,
                "volatility": volatility,
                "base_rate": base_rate,
                "quote_rate": quote_rate,
                "base_currency": base_currency,
                "quote_currency": quote_currency
            }
        }
        
    except Exception as e:
        logger.error(f"Option pricing error: {str(e)}")
        return {"status": "error", "error": str(e)}

@app.post("/api/trades/load-by-fund")
async def load_trades_by_fund(request: dict):
    """Load trades from PostgreSQL for a specific fund"""
    import psycopg2
    import psycopg2.extras
    
    try:
        fund_id = request.get('fund_id')
        if not fund_id:
            return {"status": "error", "error": "fund_id is required"}
        
        # Get PostgreSQL password from Key Vault
        env = os.environ.copy()
        if 'POSTGRES_PASSWORD' not in env:
            logger.info("Getting PostgreSQL password from Azure Key Vault...")
            try:
                import subprocess
                password = subprocess.run([
                    'az', 'keyvault', 'secret', 'show', 
                    '--vault-name', 'gzc-finma-keyvault',
                    '--name', 'postgres-connection-string',
                    '--query', 'value', 
                    '-o', 'tsv'
                ], capture_output=True, text=True, timeout=10)
                
                if password.returncode == 0:
                    connection_string = password.stdout.strip()
                    if '://' in connection_string and '@' in connection_string:
                        password_part = connection_string.split('://')[1].split('@')[0]
                        if ':' in password_part:
                            env['POSTGRES_PASSWORD'] = password_part.split(':')[1]
                        else:
                            raise ValueError("Cannot parse password from connection string")
                    else:
                        raise ValueError("Invalid connection string format")
                else:
                    raise subprocess.CalledProcessError(password.returncode, password.stderr)
                    
            except Exception as e:
                logger.error(f"❌ Failed to get password from Key Vault: {e}")
                return {"status": "error", "error": "Cannot retrieve PostgreSQL password"}
        
        # Connect to PostgreSQL
        postgres_conn = psycopg2.connect(
            host='gzcdevserver.postgres.database.azure.com',
            database='gzc_platform',
            user='mikael', 
            password=env['POSTGRES_PASSWORD'],
            port=5432,
            sslmode='require'
        )
        
        cursor = postgres_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Query FX option trades for the fund
        cursor.execute("""
            SELECT 
                trade_id,
                trade_date,
                maturity_date,
                underlying_trade_currency,
                underlying_settlement_currency,
                strike,
                quantity,
                premium,
                position,
                option_type,
                fund_id,
                trader,
                strategy_folder_id
            FROM gzc_fx_option_trade 
            WHERE fund_id = %s AND active = true
            ORDER BY trade_date DESC
        """, (fund_id,))
        
        trades = cursor.fetchall()
        postgres_conn.close()
        
        # Convert to regular dict for JSON serialization
        trades_list = [dict(trade) for trade in trades]
        
        logger.info(f"✅ Loaded {len(trades_list)} trades for fund {fund_id}")
        
        return {
            "status": "success",
            "fund_id": fund_id,
            "trades": trades_list,
            "count": len(trades_list)
        }
        
    except Exception as e:
        logger.error(f"Load trades error: {e}")
        return {"status": "error", "error": str(e)}

# Rate Curves endpoints - Database driven
def get_postgres_connection():
    """Get PostgreSQL connection using Key Vault credentials"""
    import psycopg2
    import subprocess
    
    # Get password from Key Vault if not in environment
    password = os.environ.get('POSTGRES_PASSWORD')
    if not password:
        try:
            result = subprocess.run([
                'az', 'keyvault', 'secret', 'show',
                '--vault-name', 'gzc-finma-keyvault',
                '--name', 'postgres-connection-string',
                '--query', 'value',
                '-o', 'tsv'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                connection_string = result.stdout.strip()
                if '://' in connection_string and '@' in connection_string:
                    password_part = connection_string.split('://')[1].split('@')[0]
                    if ':' in password_part:
                        password = password_part.split(':')[1]
        except Exception as e:
            logger.error(f"Failed to get password from Key Vault: {e}")
            
    if not password:
        raise ValueError("PostgreSQL password not available")
        
    return psycopg2.connect(
        host='gzcdevserver.postgres.database.azure.com',
        database='gzc_platform',
        user='mikael',
        password=password,
        port=5432,
        sslmode='require'
    )

@app.post("/api/curves/{currency}")
async def get_yield_curve(currency: str):
    """Get yield curve configuration from database and fetch live data"""
    currency = currency.upper()
    
    try:
        # Direct PostgreSQL connection
        conn_params = {
            'host': 'gzcdevserver.postgres.database.azure.com',
            'database': 'gzc_platform',
            'user': 'mikael',
            'port': 5432,
            'password': 'Ii89rra137+*',
            'sslmode': 'require'
        }
        
        import psycopg2
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Get curve definition and tickers
        cursor.execute("""
            SELECT rcd.curve_name, rcd.curve_type, rcd.methodology, rcd.primary_use,
                   bt.bloomberg_ticker, bt.description, bt.tenor, bt.tenor_numeric
            FROM rate_curve_definitions rcd
            JOIN bloomberg_tickers bt ON bt.curve_name = rcd.curve_name
            WHERE rcd.currency_code = %s AND rcd.curve_type IN ('OIS', 'IRS')
            ORDER BY 
            CASE 
                WHEN bt.bloomberg_ticker IN ('USSO15 Curncy', 'USSO20 Curncy', 'USSO30 Curncy') 
                    THEN bt.tenor_numeric * 365
                WHEN bt.tenor_numeric < 365 THEN bt.tenor_numeric
                ELSE bt.tenor_numeric
            END
        """, (currency,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not results:
            return {"success": False, "error": f"No OIS curve found for {currency}"}
        
        # Extract curve info and tickers
        curve_info = results[0]
        tickers = [row[4] for row in results]  # bloomberg_ticker column
        
        # Fetch live data from Bloomberg
        bloomberg_data = await bloomberg_reference_proxy({
            "securities": tickers,
            "fields": ["PX_LAST", "SECURITY_DES"]
        })
        
        if bloomberg_data.get('success'):
            # Build response
            curve_points = []
            
            # Create a map of ticker -> bloomberg data
            bloomberg_map = {}
            for sec_data in bloomberg_data['data']['securities_data']:
                if sec_data.get('success'):
                    bloomberg_map[sec_data['security']] = sec_data
            
            for row in results:
                ticker = row[4]  # bloomberg_ticker
                if ticker in bloomberg_map:
                    bloomberg_result = bloomberg_map[ticker]
                    tenor_numeric = row[7]  # tenor_numeric
                    
                    # Debug logging for 1M, 2M, 3M
                    if ticker in ['USSOA Curncy', 'USSOB Curncy', 'USSOC Curncy']:
                        logger.info(f"Processing short ticker: {ticker}, tenor_numeric={tenor_numeric}")
                    
                    # Fixed mapping based on ticker patterns
                    if ticker in ['SOFRRATE Index', 'ESTR Index', 'ESTRON Index', 'EUDR1T Curncy', 'SONIO/N Index', 'USDR1T Curncy']:
                        # Overnight rates - 1 day
                        tenor_days = 1
                    elif ticker == 'USSO15 Curncy':
                        tenor_days = 15 * 365  # 5475 days
                    elif ticker == 'USSO20 Curncy':
                        tenor_days = 20 * 365  # 7300 days
                    elif ticker == 'USSO30 Curncy':
                        tenor_days = 30 * 365  # 10950 days
                    elif ticker in ['USSOA Curncy', 'USSOB Curncy', 'USSOC Curncy']:
                        # USD Monthly tickers are already in days
                        tenor_days = tenor_numeric
                        logger.info(f"Set tenor_days={tenor_days} for {ticker}")
                    elif ticker.startswith('EUR') and ticker.endswith('Index'):
                        # EUR money market rates - stored in days
                        tenor_days = tenor_numeric
                    elif ticker.startswith('EUSA') and ticker.endswith('Curncy'):
                        # EUR swap rates vs 6M EURIBOR - stored as years
                        tenor_days = tenor_numeric * 365
                    elif ticker.startswith('BPSO') and ticker.endswith('Curncy'):
                        # GBP OIS swaps
                        if ticker[4].isalpha():
                            # Letters = months (BPSOA, BPSOB, etc) - stored in days
                            tenor_days = tenor_numeric
                        else:
                            # Numbers = years (BPSO1, BPSO2, etc) - stored as years
                            tenor_days = tenor_numeric * 365
                    elif ticker.startswith(('JYSO', 'CDSO', 'ADSO', 'NDSO')) and ticker.endswith('Curncy'):
                        # JPY, CAD, AUD, NZD OIS swaps
                        if ticker[4].isalpha():
                            # Letters = months - stored in days
                            tenor_days = tenor_numeric
                        else:
                            # Numbers = years - stored as years
                            tenor_days = tenor_numeric * 365
                    elif ticker.startswith(('SKSW', 'NKSW')) and ticker.endswith('Curncy'):
                        # SEK, NOK IRS swaps - stored as years
                        tenor_days = tenor_numeric * 365
                    elif ticker in ['MUTKCALM Index', 'CAONREPO Index', 'RBACOR Index', 'NZOCRS Index', 'SSARON Index']:
                        # G10 overnight rates
                        tenor_days = 1
                    elif ticker in ['STIB1W Index', 'NIBOR1W Index']:
                        # Weekly rates used as short-end proxy
                        tenor_days = 7
                    elif tenor_numeric is not None and tenor_numeric < 100:
                        # Years for other long-term tickers
                        tenor_days = tenor_numeric * 365
                    elif tenor_numeric is not None:
                        # Already in days
                        tenor_days = tenor_numeric
                    else:
                        # Skip points with missing tenor_numeric
                        logger.warning(f"Skipping {ticker} - missing tenor_numeric")
                        continue
                    
                    curve_points.append({
                        "ticker": ticker,
                        "tenor": row[6],   # tenor
                        "tenor_days": tenor_days,
                        "rate": bloomberg_result['fields'].get('PX_LAST'),
                        "description": bloomberg_result['fields'].get('SECURITY_DES', row[5])
                    })
            
            return {
                "success": True,
                "currency": currency,
                "curve_name": curve_info[0],  # curve_name
                "curve_type": curve_info[1],  # curve_type
                "methodology": curve_info[2], # methodology  
                "primary_use": curve_info[3], # primary_use
                "points": curve_points,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "error": "Failed to fetch Bloomberg data"}
            
    except Exception as e:
        logger.error(f"Rate curves error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/curves")
async def list_supported_curves():
    """List all supported yield curves"""
    return {
        "curves": [
            {
                "currency": currency,
                "name": config["name"],
                "points": len(config["tickers"])
            }
            for currency, config in RATE_CURVE_TICKERS.items()
        ]
    }

# Container/Kubernetes specific endpoints
@app.get("/ready")
async def readiness():
    """Kubernetes readiness probe"""
    return {"ready": True}

@app.get("/live")
async def liveness():
    """Kubernetes liveness probe"""
    return {"alive": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)