#!/usr/bin/env python3
"""
Simple test: Can we get any news-related data?
"""

import requests
import json

def simple_news_test():
    """Test what news-related data we can get"""
    
    print("📰 Simple Bloomberg News Test")
    print("=" * 50)
    
    # Test 1: Check if we have news sentiment or heat data
    print("\n1. Testing News Sentiment/Heat Fields:")
    
    payload = {
        "securities": ["AAPL US Equity", "TSLA US Equity", "MSFT US Equity"],
        "fields": [
            "NEWS_HEAT_AVG_DAILY",      # News heat average
            "NEWS_SENTIMENT_DAILY_AVG",  # News sentiment
            "STORY_COUNT_LAST_ONE_DAY",  # Story count
            "LAST_NEWS",                 # Last news time
            "NAME"                       # Company name
        ]
    }
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data:
                security = item['security']
                fields = item['fields']
                name = fields.get('NAME', security)
                
                print(f"\n{name}:")
                
                # Check each news field
                if 'NEWS_HEAT_AVG_DAILY' in fields:
                    print(f"  📊 News Heat: {fields['NEWS_HEAT_AVG_DAILY']}")
                    
                if 'NEWS_SENTIMENT_DAILY_AVG' in fields:
                    print(f"  😊 Sentiment: {fields['NEWS_SENTIMENT_DAILY_AVG']}")
                    
                if 'STORY_COUNT_LAST_ONE_DAY' in fields:
                    print(f"  📰 Stories Today: {fields['STORY_COUNT_LAST_ONE_DAY']}")
                    
                if 'LAST_NEWS' in fields:
                    print(f"  ⏰ Last News: {fields['LAST_NEWS']}")
                    
                # If no news fields available
                if not any(field in fields for field in ['NEWS_HEAT_AVG_DAILY', 'NEWS_SENTIMENT_DAILY_AVG', 'STORY_COUNT_LAST_ONE_DAY']):
                    print("  ❌ No news data available")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Try event-based fields
    print("\n\n2. Testing Event/Announcement Fields:")
    
    event_payload = {
        "securities": ["AAPL US Equity"],
        "fields": [
            "ANNOUNCEMENT_DT",           # Announcement date
            "DVD_HIST_ALL",             # Dividend history
            "EARN_ANN_DT_NEXT",         # Next earnings date
            "EVENT_TITLE",              # Event title
            "COMPANY_NEWS_NUM_STORIES"  # Number of news stories
        ]
    }
    
    try:
        response = requests.post(
            "http://20.172.249.92:8080/api/market-data",
            json=event_payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                item = data[0]
                fields = item['fields']
                
                print("\nAPPL Event Data:")
                for field, value in fields.items():
                    if value is not None:
                        print(f"  {field}: {value}")
                        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("\n💡 What this tells us:")
    print("If we see news heat/sentiment → We can track news impact")
    print("If we see story counts → We know how active the news is")
    print("If these fail → We need to use email/Terminal automation")


if __name__ == "__main__":
    simple_news_test()