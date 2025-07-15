#!/usr/bin/env python3
"""
Example: Bloomberg News to Cosmos DB
Demonstrates how to fetch Bloomberg news and store in Cosmos DB
"""

import os
import json
import logging
from datetime import datetime
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import sys
sys.path.append('..')
from bloomberg_client import BloombergClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BloombergNewsToCosmosDB:
    """Fetch Bloomberg news and store in Cosmos DB"""
    
    def __init__(self):
        # Initialize Bloomberg client
        self.bloomberg = BloombergClient()
        
        # Initialize Cosmos DB client
        credential = DefaultAzureCredential()
        cosmos_endpoint = "https://cosmos-research-analytics-prod.documents.azure.com:443/"
        self.cosmos_client = CosmosClient(cosmos_endpoint, credential)
        
        # Get database and container
        self.database = self.cosmos_client.get_database_client("research-analytics-db")
        self.container = self.database.get_container_client("bloomberg-news")
        
    def fetch_and_store_news(self, topics=None, hours_back=24):
        """Fetch news from Bloomberg and store in Cosmos DB"""
        
        # Fetch news
        logger.info(f"Fetching Bloomberg news for topics: {topics}")
        news_stories = self.bloomberg.get_news(
            topics=topics or ["TOP", "FX", "ECONOMIC"],
            max_stories=50,
            hours_back=hours_back
        )
        
        logger.info(f"Retrieved {len(news_stories)} stories")
        
        # Store each story
        stored_count = 0
        for story in news_stories:
            try:
                # Prepare document for Cosmos DB
                document = {
                    "id": story["story_id"],
                    "headline": story["headline"],
                    "datetime": story["datetime"],
                    "topics": story["topics"],
                    "synopsis": story.get("synopsis", ""),
                    "source": "Bloomberg Terminal",
                    "ingested_at": datetime.utcnow().isoformat(),
                    "partition_key": story["datetime"][:10]  # Date as partition key
                }
                
                # Upsert to Cosmos DB
                self.container.upsert_item(document)
                stored_count += 1
                
            except Exception as e:
                logger.error(f"Failed to store story {story['story_id']}: {e}")
                
        logger.info(f"Successfully stored {stored_count} stories in Cosmos DB")
        return stored_count
    
    def search_and_enrich(self, search_query):
        """Search for news and enrich with full story details"""
        
        # Search news
        logger.info(f"Searching for: {search_query}")
        search_results = self.bloomberg.search_news(
            query=search_query,
            max_results=20,
            days_back=7
        )
        
        enriched_stories = []
        
        # Get full details for each story
        for story in search_results.get("results", []):
            try:
                # Get full story
                full_story = self.bloomberg.get_story_detail(story["story_id"])
                
                # Store enriched story
                document = {
                    "id": full_story["story_id"],
                    "headline": full_story["headline"],
                    "body": full_story["body"],
                    "datetime": full_story["datetime"],
                    "source": full_story.get("source", "Bloomberg"),
                    "search_query": search_query,
                    "ingested_at": datetime.utcnow().isoformat(),
                    "partition_key": full_story["datetime"][:10]
                }
                
                self.container.upsert_item(document)
                enriched_stories.append(document)
                
            except Exception as e:
                logger.error(f"Failed to enrich story: {e}")
                
        logger.info(f"Enriched and stored {len(enriched_stories)} stories")
        return enriched_stories


def main():
    """Example usage"""
    processor = BloombergNewsToCosmosDB()
    
    # Example 1: Fetch and store latest news
    print("Fetching latest FX and Economic news...")
    count = processor.fetch_and_store_news(
        topics=["FX", "ECONOMIC"],
        hours_back=12
    )
    print(f"Stored {count} news stories")
    
    # Example 2: Search and enrich specific topics
    print("\nSearching for Federal Reserve news...")
    stories = processor.search_and_enrich("Federal Reserve monetary policy")
    print(f"Found and enriched {len(stories)} stories")


if __name__ == "__main__":
    main()