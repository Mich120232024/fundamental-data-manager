#!/usr/bin/env python3
"""
Get real Bloomberg headlines from the Terminal
"""

import requests
import json
from datetime import datetime
from bloomberg_client import BloombergClient

def get_bloomberg_headlines():
    """Retrieve Bloomberg headlines from the real terminal"""
    
    print("📰 Bloomberg Terminal Headlines")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Connect to Bloomberg API server
    bloomberg = BloombergClient("http://20.172.249.92:8080")
    
    # Check connection
    health = bloomberg.health_check()
    if not health.get('bloomberg_connected'):
        print("❌ Bloomberg Terminal not connected!")
        return
    
    print("✅ Connected to Bloomberg Terminal")
    print()
    
    # Get headlines for different topics
    topics_to_check = [
        ("TOP", "Top News"),
        ("FX", "Foreign Exchange"),
        ("ECONOMIC", "Economic News"),
        ("FED", "Federal Reserve"),
        ("MARKETS", "Market News"),
        ("TECH", "Technology"),
        ("COMMODITIES", "Commodities")
    ]
    
    for topic_code, topic_name in topics_to_check:
        print(f"\n📍 {topic_name} Headlines ({topic_code}):")
        print("-" * 50)
        
        try:
            # Get news for this topic
            news = bloomberg.get_news(
                topics=[topic_code],
                max_stories=5,
                hours_back=24
            )
            
            if news:
                for i, story in enumerate(news, 1):
                    print(f"\n{i}. {story.get('headline', 'No headline')}")
                    print(f"   Time: {story.get('datetime', 'Unknown')}")
                    print(f"   ID: {story.get('story_id', 'N/A')}")
                    if story.get('synopsis'):
                        print(f"   Synopsis: {story.get('synopsis')}")
            else:
                print("   No headlines available for this topic")
                
        except Exception as e:
            print(f"   Error retrieving {topic_name} news: {e}")
    
    # Try to get market-specific headlines
    print("\n\n📊 Market-Specific Headlines:")
    print("-" * 50)
    
    try:
        # Search for specific market events
        searches = [
            "Federal Reserve rate",
            "S&P 500",
            "Dollar strength",
            "Oil prices",
            "Earnings today"
        ]
        
        for search_term in searches:
            print(f"\n🔍 Searching: '{search_term}'")
            try:
                results = bloomberg.search_news(
                    query=search_term,
                    max_results=3,
                    days_back=1
                )
                
                if results and results.get('results'):
                    for story in results['results'][:2]:
                        print(f"   - {story.get('headline', 'No headline')}")
                else:
                    print("   No results found")
                    
            except Exception as e:
                print(f"   Search error: {e}")
                
    except Exception as e:
        print(f"Error with searches: {e}")
    
    # Get latest FX movements with news context
    print("\n\n💱 Current FX Rates & Movement:")
    print("-" * 50)
    
    try:
        fx_pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
        rates = bloomberg.get_fx_rates(fx_pairs)
        
        for rate in rates:
            security = rate['security']
            last = rate['fields'].get('PX_LAST', 'N/A')
            print(f"{security}: {last}")
            
    except Exception as e:
        print(f"Error getting FX rates: {e}")
    
    print("\n" + "=" * 60)
    print("📡 Live from Bloomberg Terminal on Azure VM")
    print("=" * 60)


if __name__ == "__main__":
    get_bloomberg_headlines()