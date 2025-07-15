#!/usr/bin/env python3
"""
Bloomberg News Collector
Collects news and market updates using Bloomberg API
"""

import blpapi
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Optional
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BloombergNewsCollector:
    def __init__(self):
        """Initialize Bloomberg News Collector"""
        self.session = None
        self.service = None
        
        # Bloomberg API settings
        self.host = "localhost"
        self.port = 8194
        
        # Azure Cosmos DB settings
        self.cosmos_endpoint = os.getenv(
            "COSMOS_ENDPOINT", 
            "https://cosmos-research-analytics-prod.documents.azure.com:443/"
        )
        self.cosmos_key = os.getenv("COSMOS_KEY")
        self.database_name = "bloomberg-data"
        self.container_name = "news-feed"
        
        # Initialize Cosmos client
        if self.cosmos_key:
            self.cosmos_client = CosmosClient(self.cosmos_endpoint, self.cosmos_key)
        else:
            credential = DefaultAzureCredential()
            self.cosmos_client = CosmosClient(self.cosmos_endpoint, credential)
            
    def connect_bloomberg(self) -> bool:
        """Connect to Bloomberg Terminal"""
        try:
            # Create session options
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost(self.host)
            sessionOptions.setServerPort(self.port)
            
            # Create and start session
            self.session = blpapi.Session(sessionOptions)
            
            if not self.session.start():
                logger.error("Failed to start Bloomberg session")
                return False
                
            if not self.session.openService("//blp/refdata"):
                logger.error("Failed to open Bloomberg service")
                return False
                
            self.service = self.session.getService("//blp/refdata")
            logger.info("Successfully connected to Bloomberg")
            return True
            
        except Exception as e:
            logger.error(f"Bloomberg connection error: {e}")
            return False
            
    def get_news(self, securities: List[str], categories: Optional[List[str]] = None) -> List[Dict]:
        """
        Get news for specified securities
        
        Args:
            securities: List of Bloomberg security identifiers (e.g., ["EURUSD Curncy", "SPX Index"])
            categories: Optional list of news categories to filter
            
        Returns:
            List of news items
        """
        if not self.session or not self.service:
            logger.error("Not connected to Bloomberg")
            return []
            
        try:
            # Create request
            request = self.service.createRequest("NewsBulkRequest")
            
            # Add securities
            for security in securities:
                request.append("securities", security)
                
            # Set time range (last 24 hours)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            
            request.set("startDateTime", start_time.strftime("%Y-%m-%dT%H:%M:%S"))
            request.set("endDateTime", end_time.strftime("%Y-%m-%dT%H:%M:%S"))
            
            # Add categories if specified
            if categories:
                for category in categories:
                    request.append("newsCategories", category)
                    
            # Send request
            self.session.sendRequest(request)
            
            # Process response
            news_items = []
            while True:
                event = self.session.nextEvent(500)
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    for msg in event:
                        if msg.hasElement("news"):
                            news_array = msg.getElement("news")
                            for i in range(news_array.numValues()):
                                news_item = news_array.getValue(i)
                                news_items.append({
                                    "headline": news_item.getElementAsString("headline"),
                                    "story": news_item.getElementAsString("story"),
                                    "datetime": news_item.getElementAsString("dateTime"),
                                    "category": news_item.getElementAsString("category"),
                                    "source": news_item.getElementAsString("source"),
                                    "securities": securities
                                })
                    break
                    
            logger.info(f"Retrieved {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Error getting news: {e}")
            return []
            
    def get_market_updates(self, securities: List[str], fields: List[str]) -> Dict:
        """
        Get real-time market data updates
        
        Args:
            securities: List of securities (e.g., ["EURUSD Curncy"])
            fields: List of fields (e.g., ["PX_LAST", "VOLUME"])
            
        Returns:
            Market data dictionary
        """
        if not self.session or not self.service:
            logger.error("Not connected to Bloomberg")
            return {}
            
        try:
            # Create request
            request = self.service.createRequest("ReferenceDataRequest")
            
            # Add securities and fields
            for security in securities:
                request.append("securities", security)
            for field in fields:
                request.append("fields", field)
                
            # Send request
            self.session.sendRequest(request)
            
            # Process response
            market_data = {}
            while True:
                event = self.session.nextEvent(500)
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    for msg in event:
                        security_data = msg.getElement("securityData")
                        for i in range(security_data.numValues()):
                            security = security_data.getValue(i)
                            ticker = security.getElementAsString("security")
                            field_data = security.getElement("fieldData")
                            
                            market_data[ticker] = {}
                            for field in fields:
                                if field_data.hasElement(field):
                                    market_data[ticker][field] = field_data.getElementValue(field)
                    break
                    
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {}
            
    def save_to_cosmos(self, data: Dict, data_type: str = "news"):
        """Save data to Cosmos DB"""
        try:
            database = self.cosmos_client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            
            # Add metadata
            data["id"] = f"{data_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            data["timestamp"] = datetime.now().isoformat()
            data["dataType"] = data_type
            data["partitionKey"] = data_type.upper()
            
            # Insert document
            container.create_item(body=data)
            logger.info(f"Saved {data_type} to Cosmos DB")
            
        except Exception as e:
            logger.error(f"Error saving to Cosmos DB: {e}")
            # Fallback to local file
            filename = f"bloomberg_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved to local file: {filename}")
            
    def collect_daily_summary(self):
        """Collect daily market summary"""
        logger.info("Starting daily market summary collection")
        
        # Define what to collect
        fx_pairs = ["EURUSD Curncy", "GBPUSD Curncy", "USDJPY Curncy"]
        indices = ["SPX Index", "DJI Index", "NKY Index"]
        commodities = ["CL1 Comdty", "GC1 Comdty"]
        
        all_securities = fx_pairs + indices + commodities
        
        # Get news
        news = self.get_news(all_securities)
        
        # Get market data
        market_fields = ["PX_LAST", "PX_OPEN", "PX_HIGH", "PX_LOW", "VOLUME", "CHG_PCT_1D"]
        market_data = self.get_market_updates(all_securities, market_fields)
        
        # Create summary
        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "news_count": len(news),
            "top_news": news[:5] if news else [],
            "market_data": market_data,
            "fx_summary": {ticker: market_data.get(ticker, {}) for ticker in fx_pairs},
            "indices_summary": {ticker: market_data.get(ticker, {}) for ticker in indices},
            "commodities_summary": {ticker: market_data.get(ticker, {}) for ticker in commodities}
        }
        
        # Save to Cosmos DB
        self.save_to_cosmos(summary, "daily-summary")
        
        return summary
        
    def run_continuous_collection(self, interval_minutes: int = 15):
        """Run continuous news collection"""
        import time
        
        logger.info(f"Starting continuous collection every {interval_minutes} minutes")
        
        while True:
            try:
                # Collect data
                summary = self.collect_daily_summary()
                
                # Log summary
                logger.info(f"Collected {summary['news_count']} news items")
                logger.info(f"Market data: {len(summary['market_data'])} securities")
                
                # Wait for next interval
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous collection")
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                time.sleep(60)  # Wait 1 minute before retry
                
    def disconnect(self):
        """Disconnect from Bloomberg"""
        if self.session:
            self.session.stop()
            logger.info("Disconnected from Bloomberg")


def main():
    """Main function"""
    collector = BloombergNewsCollector()
    
    # Connect to Bloomberg
    if not collector.connect_bloomberg():
        logger.error("Failed to connect to Bloomberg Terminal")
        logger.info("Make sure Bloomberg Terminal is running and logged in")
        return
        
    try:
        # Run collection
        print("\nBloomberg News Collector")
        print("=" * 50)
        print("1. Collect daily summary once")
        print("2. Run continuous collection (every 15 min)")
        print("3. Test news collection")
        print("4. Test market data")
        
        choice = input("\nSelect option (1-4): ")
        
        if choice == "1":
            summary = collector.collect_daily_summary()
            print(f"\nCollected {summary['news_count']} news items")
            print(f"Market data for {len(summary['market_data'])} securities")
            
        elif choice == "2":
            collector.run_continuous_collection()
            
        elif choice == "3":
            news = collector.get_news(["EURUSD Curncy", "SPX Index"])
            print(f"\nFound {len(news)} news items")
            for item in news[:3]:
                print(f"\n{item['datetime']}: {item['headline']}")
                
        elif choice == "4":
            data = collector.get_market_updates(
                ["EURUSD Curncy", "SPX Index"], 
                ["PX_LAST", "CHG_PCT_1D"]
            )
            print("\nMarket Data:")
            for security, fields in data.items():
                print(f"\n{security}:")
                for field, value in fields.items():
                    print(f"  {field}: {value}")
                    
    finally:
        collector.disconnect()


if __name__ == "__main__":
    main()