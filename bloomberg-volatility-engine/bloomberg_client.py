#!/usr/bin/env python3
"""
Bloomberg API Client
Client library for connecting to the Bloomberg API Server from anywhere in the system
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class BloombergClient:
    """Client for accessing Bloomberg API Server"""
    
    def __init__(self, server_url: str = None, timeout: int = 30):
        """
        Initialize Bloomberg client
        
        Args:
            server_url: URL of Bloomberg API server (default from env or VM IP)
            timeout: Request timeout in seconds
        """
        # Get server URL from environment or use VM IP
        self.server_url = server_url or os.getenv(
            "BLOOMBERG_API_SERVER", 
            "http://10.225.1.5:8080"  # Internal IP of Bloomberg VM
        )
        
        if not self.server_url.startswith("http"):
            self.server_url = f"http://{self.server_url}"
            
        self.timeout = timeout
        
        # Setup session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"Bloomberg client initialized with server: {self.server_url}")
    
    def health_check(self) -> Dict:
        """Check if Bloomberg API server is healthy"""
        try:
            response = self.session.get(
                f"{self.server_url}/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def get_news(
        self, 
        topics: List[str] = None, 
        max_stories: int = 10,
        hours_back: int = 24
    ) -> List[Dict]:
        """
        Get Bloomberg news stories
        
        Args:
            topics: List of topics (default: ["TOP", "FX", "ECONOMIC"])
            max_stories: Maximum number of stories to retrieve
            hours_back: How many hours back to search
            
        Returns:
            List of news stories
        """
        if topics is None:
            topics = ["TOP", "FX", "ECONOMIC"]
            
        payload = {
            "topics": topics,
            "max_stories": max_stories,
            "hours_back": hours_back
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/api/news",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get news: {e}")
            raise
    
    def get_story_detail(self, story_id: str) -> Dict:
        """Get full details of a specific news story"""
        try:
            response = self.session.post(
                f"{self.server_url}/api/news/story/{story_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get story detail: {e}")
            raise
    
    def search_news(
        self, 
        query: str, 
        max_results: int = 20, 
        days_back: int = 7
    ) -> Dict:
        """
        Search Bloomberg news
        
        Args:
            query: Search query
            max_results: Maximum number of results
            days_back: Number of days to search back
            
        Returns:
            Search results
        """
        params = {
            "query": query,
            "max_results": max_results,
            "days_back": days_back
        }
        
        try:
            response = self.session.get(
                f"{self.server_url}/api/news/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to search news: {e}")
            raise
    
    def get_market_data(
        self, 
        securities: List[str], 
        fields: List[str]
    ) -> List[Dict]:
        """
        Get market data for securities
        
        Args:
            securities: List of Bloomberg securities (e.g., ["EURUSD Curncy"])
            fields: List of fields (e.g., ["PX_LAST", "PX_BID"])
            
        Returns:
            List of market data responses
        """
        payload = {
            "securities": securities,
            "fields": fields
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/api/market-data",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            raise
    
    def get_fx_rates(self, pairs: List[str] = None) -> List[Dict]:
        """
        Get FX rates
        
        Args:
            pairs: List of currency pairs (default: ["EURUSD", "GBPUSD", "USDJPY"])
            
        Returns:
            List of FX rates
        """
        if pairs is None:
            pairs = ["EURUSD", "GBPUSD", "USDJPY"]
            
        params = {"pairs": pairs}
        
        try:
            response = self.session.get(
                f"{self.server_url}/api/fx/rates",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get FX rates: {e}")
            raise


# Example usage functions
def example_get_latest_news():
    """Example: Get latest news"""
    client = BloombergClient()
    
    # Check health
    health = client.health_check()
    print(f"Server health: {health}")
    
    # Get news
    news = client.get_news(
        topics=["FX", "ECONOMIC"],
        max_stories=5,
        hours_back=12
    )
    
    print(f"\nFound {len(news)} news stories:")
    for story in news:
        print(f"- {story['datetime']}: {story['headline']}")
        
    return news


def example_search_news():
    """Example: Search for specific news"""
    client = BloombergClient()
    
    results = client.search_news(
        query="Federal Reserve inflation",
        max_results=10,
        days_back=3
    )
    
    print(f"Search results for '{results['query']}':")
    print(f"Found {results['count']} stories")
    
    return results


def example_get_fx_rates():
    """Example: Get FX rates"""
    client = BloombergClient()
    
    rates = client.get_fx_rates(["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"])
    
    print("\nCurrent FX Rates:")
    for rate in rates:
        security = rate['security']
        fields = rate['fields']
        print(f"{security}: {fields.get('PX_LAST', 'N/A')}")
        
    return rates


if __name__ == "__main__":
    # Run examples
    print("Bloomberg Client Examples")
    print("=" * 50)
    
    try:
        # Test connection
        client = BloombergClient()
        health = client.health_check()
        
        if health.get("bloomberg_connected"):
            print("✓ Connected to Bloomberg API Server")
            print(f"  Server URL: {client.server_url}")
            print(f"  Bloomberg Terminal: Connected")
            
            # Run examples
            print("\n1. Getting latest news...")
            example_get_latest_news()
            
            print("\n2. Getting FX rates...")
            example_get_fx_rates()
            
        else:
            print("✗ Bloomberg Terminal not connected on server")
            
    except Exception as e:
        print(f"✗ Error: {e}")