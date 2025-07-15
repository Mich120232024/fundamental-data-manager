#!/usr/bin/env python3
"""
General Financial News Collector
Collects financial news from various free sources
Can run independently or alongside Bloomberg integration
"""

import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class NewsSource:
    """News source configuration"""
    name: str
    url: str
    source_type: str  # 'rss', 'api', 'web'
    category: str

class GeneralNewsCollector:
    def __init__(self):
        """Initialize the news collector"""
        
        # Azure Cosmos DB settings
        self.cosmos_endpoint = os.getenv(
            "COSMOS_ENDPOINT", 
            "https://cosmos-research-analytics-prod.documents.azure.com:443/"
        )
        self.cosmos_key = os.getenv("COSMOS_KEY")
        self.database_name = "market-intelligence"
        self.container_name = "news-feed"
        
        # Initialize Cosmos client if credentials available
        self.cosmos_client = None
        if self.cosmos_key:
            self.cosmos_client = CosmosClient(self.cosmos_endpoint, self.cosmos_key)
            logger.info("Cosmos DB client initialized")
        
        # Define news sources
        self.sources = [
            # Financial RSS Feeds
            NewsSource(
                name="Reuters Markets",
                url="https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best",
                source_type="rss",
                category="markets"
            ),
            NewsSource(
                name="Financial Times",
                url="https://www.ft.com/markets?format=rss",
                source_type="rss",
                category="markets"
            ),
            NewsSource(
                name="Bloomberg RSS",
                url="https://feeds.bloomberg.com/markets/news.rss",
                source_type="rss",
                category="markets"
            ),
            NewsSource(
                name="WSJ Markets",
                url="https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
                source_type="rss",
                category="markets"
            ),
            NewsSource(
                name="CNBC Markets",
                url="https://www.cnbc.com/id/10001147/device/rss/rss.html",
                source_type="rss",
                category="markets"
            ),
            NewsSource(
                name="MarketWatch",
                url="http://feeds.marketwatch.com/marketwatch/realtimeheadlines",
                source_type="rss",
                category="markets"
            ),
            # Central Banks
            NewsSource(
                name="Federal Reserve",
                url="https://www.federalreserve.gov/feeds/press_all.xml",
                source_type="rss",
                category="central_banks"
            ),
            NewsSource(
                name="ECB News",
                url="https://www.ecb.europa.eu/rss/press.html",
                source_type="rss",
                category="central_banks"
            ),
            # Crypto News
            NewsSource(
                name="CoinDesk",
                url="https://www.coindesk.com/arc/outboundfeeds/rss/",
                source_type="rss",
                category="crypto"
            ),
            # Economic Data
            NewsSource(
                name="Trading Economics",
                url="https://tradingeconomics.com/rss/news.aspx",
                source_type="rss",
                category="economics"
            )
        ]
        
    async def fetch_rss_feed(self, source: NewsSource) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source.url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        news_items = []
                        for entry in feed.entries[:10]:  # Limit to 10 items per source
                            # Parse publication date
                            pub_date = None
                            if hasattr(entry, 'published_parsed'):
                                pub_date = datetime.fromtimestamp(
                                    entry.published_parsed.tm_sec
                                )
                            elif hasattr(entry, 'updated_parsed'):
                                pub_date = datetime.fromtimestamp(
                                    entry.updated_parsed.tm_sec
                                )
                            else:
                                pub_date = datetime.now()
                                
                            # Skip old news (>24 hours)
                            if pub_date < datetime.now() - timedelta(hours=24):
                                continue
                                
                            news_items.append({
                                "source": source.name,
                                "category": source.category,
                                "title": entry.get('title', 'No title'),
                                "summary": entry.get('summary', '')[:500],  # Limit summary length
                                "link": entry.get('link', ''),
                                "published": pub_date.isoformat(),
                                "tags": [tag.term for tag in entry.get('tags', [])][:5]
                            })
                            
                        logger.info(f"Fetched {len(news_items)} items from {source.name}")
                        return news_items
                        
        except Exception as e:
            logger.error(f"Error fetching {source.name}: {e}")
            return []
            
    async def collect_all_news(self) -> Dict:
        """Collect news from all sources"""
        logger.info("Starting news collection from all sources")
        
        # Create tasks for all RSS feeds
        tasks = []
        for source in self.sources:
            if source.source_type == "rss":
                tasks.append(self.fetch_rss_feed(source))
                
        # Gather all results
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_news = []
        for news_list in results:
            all_news.extend(news_list)
            
        # Sort by publication date
        all_news.sort(key=lambda x: x['published'], reverse=True)
        
        # Create summary by category
        category_summary = {}
        for item in all_news:
            category = item['category']
            if category not in category_summary:
                category_summary[category] = []
            category_summary[category].append(item)
            
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(all_news),
            "sources_checked": len(self.sources),
            "news_by_category": category_summary,
            "latest_news": all_news[:20],  # Top 20 most recent
            "market_sentiment": self.analyze_sentiment(all_news)
        }
        
        logger.info(f"Collected {len(all_news)} total news items")
        return summary
        
    def analyze_sentiment(self, news_items: List[Dict]) -> Dict:
        """Simple sentiment analysis based on keywords"""
        positive_words = [
            'gains', 'rises', 'rally', 'surge', 'boost', 'growth', 
            'recovery', 'bullish', 'strong', 'record', 'high'
        ]
        negative_words = [
            'falls', 'drops', 'decline', 'slump', 'weak', 'concern',
            'fear', 'bearish', 'crash', 'low', 'recession'
        ]
        
        positive_count = 0
        negative_count = 0
        
        for item in news_items:
            text = (item['title'] + ' ' + item['summary']).lower()
            
            for word in positive_words:
                if word in text:
                    positive_count += 1
                    break
                    
            for word in negative_words:
                if word in text:
                    negative_count += 1
                    break
                    
        total = len(news_items)
        return {
            "positive_ratio": round(positive_count / total, 2) if total > 0 else 0,
            "negative_ratio": round(negative_count / total, 2) if total > 0 else 0,
            "neutral_ratio": round((total - positive_count - negative_count) / total, 2) if total > 0 else 0,
            "overall": "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral"
        }
        
    def save_to_cosmos(self, data: Dict):
        """Save news summary to Cosmos DB"""
        if not self.cosmos_client:
            logger.warning("Cosmos DB not configured, saving locally")
            self.save_to_file(data)
            return
            
        try:
            database = self.cosmos_client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            
            # Add metadata
            data["id"] = f"news-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            data["partitionKey"] = "NEWS_SUMMARY"
            
            # Insert document
            container.create_item(body=data)
            logger.info("Saved news summary to Cosmos DB")
            
        except Exception as e:
            logger.error(f"Error saving to Cosmos DB: {e}")
            self.save_to_file(data)
            
    def save_to_file(self, data: Dict):
        """Save news summary to local file"""
        filename = f"news_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved news summary to {filename}")
        
    def format_summary_report(self, summary: Dict) -> str:
        """Format news summary as readable report"""
        report = []
        report.append("# Financial News Summary")
        report.append(f"Generated: {summary['timestamp']}")
        report.append(f"Total Items: {summary['total_items']}")
        report.append(f"Market Sentiment: {summary['market_sentiment']['overall'].upper()}")
        report.append("")
        
        # Category summaries
        for category, items in summary['news_by_category'].items():
            report.append(f"\n## {category.replace('_', ' ').title()} ({len(items)} items)")
            report.append("")
            
            # Show top 3 from each category
            for item in items[:3]:
                report.append(f"**{item['source']}** - {item['published']}")
                report.append(f"{item['title']}")
                if item['summary']:
                    report.append(f"> {item['summary'][:200]}...")
                report.append(f"[Read more]({item['link']})")
                report.append("")
                
        # Market sentiment details
        sentiment = summary['market_sentiment']
        report.append("\n## Market Sentiment Analysis")
        report.append(f"- Positive: {sentiment['positive_ratio']*100:.0f}%")
        report.append(f"- Negative: {sentiment['negative_ratio']*100:.0f}%")
        report.append(f"- Neutral: {sentiment['neutral_ratio']*100:.0f}%")
        
        return "\n".join(report)
        
    async def run_continuous(self, interval_minutes: int = 30):
        """Run continuous news collection"""
        logger.info(f"Starting continuous collection every {interval_minutes} minutes")
        
        while True:
            try:
                # Collect news
                summary = await self.collect_all_news()
                
                # Save to database/file
                self.save_to_cosmos(summary)
                
                # Generate report
                report = self.format_summary_report(summary)
                
                # Save report
                with open("latest_news_report.md", 'w') as f:
                    f.write(report)
                    
                logger.info(f"Collection complete. Next run in {interval_minutes} minutes")
                
                # Wait for next interval
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous collection")
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry


async def main():
    """Main function"""
    collector = GeneralNewsCollector()
    
    print("\nFinancial News Collector")
    print("=" * 50)
    print("1. Collect news once")
    print("2. Run continuous collection (every 30 min)")
    print("3. Generate report only")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        summary = await collector.collect_all_news()
        collector.save_to_cosmos(summary)
        report = collector.format_summary_report(summary)
        print("\n" + report)
        with open("news_report.md", 'w') as f:
            f.write(report)
        print("\nReport saved to news_report.md")
        
    elif choice == "2":
        await collector.run_continuous()
        
    elif choice == "3":
        # Try to load latest summary
        import glob
        files = glob.glob("news_summary_*.json")
        if files:
            latest = max(files)
            with open(latest, 'r') as f:
                summary = json.load(f)
            report = collector.format_summary_report(summary)
            print("\n" + report)
        else:
            print("No saved summaries found. Run collection first.")


if __name__ == "__main__":
    asyncio.run(main())