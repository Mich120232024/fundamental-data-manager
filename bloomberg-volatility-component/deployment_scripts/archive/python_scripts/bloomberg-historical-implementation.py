# Bloomberg Historical Data Implementation
# Based on research findings for FX volatility surface data

import blpapi
from datetime import datetime, timedelta
from typing import List, Dict, Any

class BloombergHistoricalAPI:
    """Bloomberg Historical Data API for FX Volatility Surface"""
    
    def __init__(self):
        self.session = None
        self.service = None
        
    def start_session(self):
        """Initialize Bloomberg session"""
        try:
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost('localhost')
            sessionOptions.setServerPort(8194)
            
            self.session = blpapi.Session(sessionOptions)
            if not self.session.start():
                raise Exception("Failed to start Bloomberg session")
                
            if not self.session.openService("//blp/refdata"):
                raise Exception("Failed to open Bloomberg reference data service")
                
            self.service = self.session.getService("//blp/refdata")
            return True
            
        except Exception as e:
            raise Exception(f"Bloomberg connection failed: {e}")
    
    def get_10d_butterfly_historical(self, currency_pair: str, tenor: str, days_back: int = 10) -> Dict[str, Any]:
        """
        Get 10D Butterfly historical data for the last N days
        
        Args:
            currency_pair: e.g., "EURUSD"
            tenor: e.g., "1M", "3M", "6M"
            days_back: Number of days to retrieve (default 10)
            
        Returns:
            Dict with historical data points
        """
        if not self.session or not self.service:
            self.start_session()
        
        # Construct Bloomberg security for 10D Butterfly
        security = f"{currency_pair}10B{tenor} BGN Curncy"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back + 5)  # Extra days to account for weekends
        
        return self._get_historical_data(
            security=security,
            fields=["PX_LAST", "PX_HIGH", "PX_LOW", "PX_OPEN", "CHG_PCT_1D"],
            start_date=start_date,
            end_date=end_date
        )
    
    def get_volatility_surface_historical(self, currency_pair: str, tenor: str, days_back: int = 10) -> Dict[str, Any]:
        """
        Get complete volatility surface historical data
        
        Returns:
            Dict with ATM, 10D RR, 10D BF, 25D RR, 25D BF historical data
        """
        if not self.session or not self.service:
            self.start_session()
        
        # All volatility surface components
        securities = [
            f"{currency_pair}V{tenor} BGN Curncy",      # ATM
            f"{currency_pair}10R{tenor} BGN Curncy",    # 10D Risk Reversal
            f"{currency_pair}10B{tenor} BGN Curncy",    # 10D Butterfly
            f"{currency_pair}25R{tenor} BGN Curncy",    # 25D Risk Reversal
            f"{currency_pair}25B{tenor} BGN Curncy"     # 25D Butterfly
        ]
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back + 5)
        
        surface_data = {}
        for security in securities:
            component = self._extract_component_name(security)
            surface_data[component] = self._get_historical_data(
                security=security,
                fields=["PX_LAST", "PX_BID", "PX_ASK"],
                start_date=start_date,
                end_date=end_date
            )
        
        return surface_data
    
    def _get_historical_data(self, security: str, fields: List[str], start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Internal method for historical data requests"""
        try:
            # Create historical data request
            request = self.service.createRequest("HistoricalDataRequest")
            
            # Add security and fields
            request.getElement("securities").appendValue(security)
            for field in fields:
                request.getElement("fields").appendValue(field)
                
            # Set date range
            request.set("startDate", start_date.strftime("%Y%m%d"))
            request.set("endDate", end_date.strftime("%Y%m%d"))
            request.set("periodicitySelection", "DAILY")
            
            # Send request
            self.session.sendRequest(request)
            
            # Process response
            historical_data = []
            
            while True:
                event = self.session.nextEvent(5000)  # 5 second timeout
                
                for msg in event:
                    if msg.messageType() == "HistoricalDataResponse":
                        securityData = msg.getElement("securityData")
                        
                        if securityData.hasElement("fieldData"):
                            fieldDataArray = securityData.getElement("fieldData")
                            
                            for i in range(fieldDataArray.numValues()):
                                fieldData = fieldDataArray.getValueAsElement(i)
                                date_str = fieldData.getElement("date").getValueAsString()
                                
                                data_point = {"date": date_str}
                                
                                for field in fields:
                                    if fieldData.hasElement(field):
                                        value = fieldData.getElement(field).getValue()
                                        data_point[field] = float(value) if isinstance(value, (int, float)) else value
                                        
                                historical_data.append(data_point)
                                
                        if securityData.hasElement("securityError"):
                            error = securityData.getElement("securityError")
                            return {
                                "error": error.getElement("message").getValueAsString(),
                                "security": security
                            }
                            
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
                    
            return {
                "security": security,
                "fields": fields,
                "start_date": start_date.strftime("%Y%m%d"),
                "end_date": end_date.strftime("%Y%m%d"),
                "data_points": len(historical_data),
                "historical_data": historical_data
            }
            
        except Exception as e:
            return {
                "error": f"Historical data error: {str(e)}",
                "security": security
            }
    
    def _extract_component_name(self, security: str) -> str:
        """Extract component name from Bloomberg security"""
        if "V" in security and "BGN Curncy" in security:
            return "ATM"
        elif "10R" in security:
            return "10D_RR"
        elif "10B" in security:
            return "10D_BF"
        elif "25R" in security:
            return "25D_RR"
        elif "25B" in security:
            return "25D_BF"
        else:
            return "UNKNOWN"


# Example usage for your specific question:
def get_eurusd_10d_butterfly_last_10_days():
    """
    Example: Get EURUSD 10D Butterfly for last 10 days
    """
    bloomberg = BloombergHistoricalAPI()
    
    # Your specific request: 10D butterfly for last 10 days
    result = bloomberg.get_10d_butterfly_historical(
        currency_pair="EURUSD",
        tenor="1M",
        days_back=10
    )
    
    print(f"Security: {result['security']}")
    print(f"Data points: {result['data_points']}")
    print(f"Date range: {result['start_date']} to {result['end_date']}")
    print("\nHistorical data:")
    
    for data_point in result['historical_data']:
        print(f"Date: {data_point['date']}, Value: {data_point.get('PX_LAST', 'N/A')}%")
    
    return result


# FastAPI endpoint implementation
from fastapi import FastAPI, Depends
from pydantic import BaseModel

class HistoricalVolatilityRequest(BaseModel):
    currency_pair: str = "EURUSD"
    tenor: str = "1M" 
    component: str = "10D_BF"  # 10D_BF, 25D_BF, 10D_RR, 25D_RR, ATM
    days_back: int = 10

@app.post('/api/bloomberg/historical/volatility')
async def get_historical_volatility(
    request: HistoricalVolatilityRequest,
    api_key: str = Depends(validate_api_key)
):
    """
    Get historical FX volatility data
    
    Example: Get 10D butterfly for last 10 days
    POST /api/bloomberg/historical/volatility
    {
        "currency_pair": "EURUSD",
        "tenor": "1M",
        "component": "10D_BF",
        "days_back": 10
    }
    """
    query_id = f'hist_vol_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    
    try:
        bloomberg = BloombergHistoricalAPI()
        
        if request.component == "10D_BF":
            data = bloomberg.get_10d_butterfly_historical(
                request.currency_pair, 
                request.tenor, 
                request.days_back
            )
        elif request.component == "SURFACE":
            data = bloomberg.get_volatility_surface_historical(
                request.currency_pair,
                request.tenor,
                request.days_back
            )
        else:
            # Single component request
            security = f"{request.currency_pair}{request.component.replace('_', '')}{request.tenor} BGN Curncy"
            data = bloomberg._get_historical_data(
                security=security,
                fields=["PX_LAST", "PX_BID", "PX_ASK"],
                start_date=datetime.now() - timedelta(days=request.days_back + 5),
                end_date=datetime.now()
            )
        
        return {
            "success": True,
            "data": data,
            "query_id": query_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query_id": query_id
        }


if __name__ == "__main__":
    # Test the implementation
    result = get_eurusd_10d_butterfly_last_10_days()
    print(result)