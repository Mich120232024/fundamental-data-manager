#!/usr/bin/env python3
"""
Example: Using Bloomberg API Server from your system
This shows how any part of your system can access Bloomberg data
"""

import json
from bloomberg_client import BloombergClient
from datetime import datetime

def example_news_monitoring():
    """Example: Monitor Bloomberg news for specific topics"""
    
    print("📰 Bloomberg News Monitoring Example")
    print("=" * 50)
    
    # Initialize Bloomberg client
    bloomberg = BloombergClient("http://20.172.249.92:8080")
    
    # Check server health
    health = bloomberg.health_check()
    print(f"Server Status: {health['status']}")
    print(f"Server Version: {health.get('version', 'Unknown')}\n")
    
    # Get latest FX news
    print("Latest FX News:")
    fx_news = bloomberg.get_news(topics=["FX"], max_stories=5)
    for story in fx_news[:3]:
        print(f"- {story['datetime']}: {story['headline']}")
        if story.get('synopsis'):
            print(f"  Synopsis: {story['synopsis']}")
    
    # Get current FX rates
    print("\nCurrent FX Rates:")
    fx_rates = bloomberg.get_fx_rates(["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"])
    for rate in fx_rates:
        security = rate['security']
        last_price = rate['fields']['PX_LAST']
        print(f"- {security}: {last_price}")
    
    # Get market data for specific securities
    print("\nMarket Data:")
    market_data = bloomberg.get_market_data(
        securities=["EURUSD Curncy", "SPX Index", "CL1 Comdty"],
        fields=["PX_LAST", "PX_BID", "PX_ASK"]
    )
    
    for data in market_data:
        security = data['security']
        fields = data['fields']
        print(f"\n{security}:")
        for field, value in fields.items():
            print(f"  {field}: {value}")
    
    # Search for specific news
    print("\n\nSearching for Federal Reserve news:")
    search_results = bloomberg.search_news(
        query="Federal Reserve monetary policy",
        max_results=5,
        days_back=7
    )
    
    print(f"Found {search_results.get('count', 0)} stories")
    
    print("\n" + "=" * 50)
    print("✅ Bloomberg data successfully retrieved!")
    print("\nThis example shows how to:")
    print("1. Get latest news by topic")
    print("2. Retrieve current FX rates")
    print("3. Get market data for any security")
    print("4. Search news archives")
    print("\nIntegrate this into your system for real-time market data!")


def example_automated_monitoring():
    """Example: Automated monitoring with alerts"""
    
    print("\n\n🤖 Automated Monitoring Example")
    print("=" * 50)
    
    bloomberg = BloombergClient("http://20.172.249.92:8080")
    
    # Define monitoring thresholds
    fx_alerts = {
        "EURUSD": {"min": 1.08, "max": 1.12},
        "GBPUSD": {"min": 1.25, "max": 1.30},
        "USDJPY": {"min": 145.0, "max": 150.0}
    }
    
    print("Monitoring FX rates for alerts...")
    
    # Check current rates
    rates = bloomberg.get_fx_rates(list(fx_alerts.keys()))
    
    alerts = []
    for rate in rates:
        pair = rate['security'].replace(' Curncy', '')
        current = rate['fields']['PX_LAST']
        thresholds = fx_alerts.get(pair, {})
        
        if current < thresholds.get('min', 0):
            alerts.append(f"🔴 {pair} below minimum: {current} < {thresholds['min']}")
        elif current > thresholds.get('max', 999):
            alerts.append(f"🔴 {pair} above maximum: {current} > {thresholds['max']}")
        else:
            print(f"✅ {pair}: {current} (within range)")
    
    if alerts:
        print("\n⚠️  ALERTS:")
        for alert in alerts:
            print(alert)
    
    # Check for important news
    print("\n\nChecking for market-moving news...")
    important_topics = ["FED", "ECB", "CRISIS", "BREAKING"]
    
    for topic in important_topics:
        news = bloomberg.get_news(topics=[topic], max_stories=1, hours_back=1)
        if news:
            print(f"📢 {topic} NEWS: {news[0]['headline']}")
    
    print("\n✅ Automated monitoring complete!")
    print("This could run every minute to alert on market changes.")


if __name__ == "__main__":
    # Run examples
    example_news_monitoring()
    example_automated_monitoring()