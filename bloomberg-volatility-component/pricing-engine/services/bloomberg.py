"""Bloomberg API client for market data"""
import httpx
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BloombergClient:
    """Client for fetching market data from Bloomberg API"""
    
    def __init__(self, base_url: str = "http://20.172.249.92:8080"):
        self.base_url = base_url
        self.headers = {
            "Authorization": "Bearer test",
            "Content-Type": "application/json"
        }
        
    async def get_spot_rates(self, pairs: List[str]) -> Dict[str, Dict]:
        """Get spot rates for currency pairs"""
        securities = [f"{pair} Curncy" for pair in pairs]
        return await self._fetch_reference_data(securities, ["PX_LAST", "PX_BID", "PX_ASK"])
    
    async def get_forward_points(self, pairs: List[str], tenors: List[str]) -> Dict[str, Dict]:
        """Get forward points for currency pairs and tenors"""
        securities = []
        for pair in pairs:
            for tenor in tenors:
                # EURUSD1M Curncy format
                securities.append(f"{pair}{tenor} Curncy")
        
        return await self._fetch_reference_data(securities, ["PX_LAST", "PX_BID", "PX_ASK"])
    
    async def get_interest_rates(self, currencies: List[str], tenors: List[str]) -> Dict[str, Dict]:
        """Get interest rates for currencies and tenors"""
        securities = []
        for ccy in currencies:
            for tenor in tenors:
                # Try multiple formats
                if tenor == "ON":
                    securities.append(f"{ccy}DR1T Curncy")  # Tomorrow/Next
                else:
                    securities.append(f"{ccy}000{tenor} Index")  # e.g., US0001M Index
        
        return await self._fetch_reference_data(securities, ["PX_LAST", "PX_BID", "PX_ASK"])
    
    async def get_volatility_surface(self, pair: str, tenors: List[str]) -> Dict[str, Dict]:
        """Get volatility surface data (ATM, RR, BF)"""
        securities = []
        
        for tenor in tenors:
            # ATM
            if tenor == "ON":
                securities.append(f"{pair}VON Curncy")
            else:
                securities.append(f"{pair}V{tenor} BGN Curncy")
            
            # Risk Reversals and Butterflies for each delta
            for delta in [5, 10, 15, 25, 35]:
                securities.append(f"{pair}{delta}R{tenor} BGN Curncy")
                securities.append(f"{pair}{delta}B{tenor} BGN Curncy")
        
        return await self._fetch_reference_data(securities, ["PX_LAST", "PX_BID", "PX_ASK"])
    
    async def _fetch_reference_data(self, securities: List[str], fields: List[str]) -> Dict[str, Dict]:
        """Fetch reference data from Bloomberg API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/bloomberg/reference",
                    json={"securities": securities, "fields": fields},
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                if not data.get("success"):
                    raise Exception(f"Bloomberg API error: {data.get('error', 'Unknown error')}")
                
                # Convert to dict for easier lookup
                result = {}
                for item in data["data"]["securities_data"]:
                    if item["success"]:
                        result[item["security"]] = item["fields"]
                    else:
                        logger.warning(f"Failed to fetch {item['security']}: {item.get('error')}")
                
                return result
                
            except Exception as e:
                logger.error(f"Bloomberg API request failed: {e}")
                raise