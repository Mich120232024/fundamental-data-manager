#!/usr/bin/env python3
"""
Simple news collector test - minimal dependencies
"""
import urllib.request
import json
from datetime import datetime

def fetch_news_simple():
    """Fetch news using only standard library"""
    print("Simple News Fetcher")
    print("=" * 50)
    
    # Example: Fetch from a simple JSON API (if available)
    # For now, let's create a mock response
    
    mock_news = {
        "timestamp": datetime.now().isoformat(),
        "source": "Mock News Feed",
        "items": [
            {
                "title": "Markets Rally on Positive Economic Data",
                "summary": "Stock markets rose today following better than expected GDP numbers...",
                "published": datetime.now().isoformat(),
                "category": "markets"
            },
            {
                "title": "Fed Maintains Interest Rates",
                "summary": "The Federal Reserve decided to keep rates unchanged...",
                "published": datetime.now().isoformat(),
                "category": "central_banks"
            },
            {
                "title": "EUR/USD Breaks 1.10 Level",
                "summary": "The euro strengthened against the dollar...",
                "published": datetime.now().isoformat(),
                "category": "forex"
            }
        ]
    }
    
    # Save to file
    filename = f"test_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(mock_news, f, indent=2)
    
    print(f"\nCreated mock news feed with {len(mock_news['items'])} items")
    print(f"Saved to: {filename}")
    
    # Display news
    print("\nLatest News:")
    print("-" * 50)
    for item in mock_news['items']:
        print(f"\n📰 {item['title']}")
        print(f"   Category: {item['category']}")
        print(f"   {item['summary']}")
    
    return mock_news

if __name__ == "__main__":
    fetch_news_simple()