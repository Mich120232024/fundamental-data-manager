#!/usr/bin/env python3
"""
Bloomberg API Server
Runs on Azure VM to provide Bloomberg Terminal access to the entire system
Exposes REST API endpoints for news, market data, and other Bloomberg queries
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import blpapi
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient
from azure.eventhub import EventHubProducerClient, EventData
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Bloomberg API Server",
    description="Central Bloomberg Terminal access for the entire system",
    version="1.0.0"
)

# Enable CORS for system-wide access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bloomberg session management
class BloombergSession:
    def __init__(self):
        self.session = None
        self.service = None
        self.connected = False
        
    def connect(self):
        """Connect to Bloomberg Terminal"""
        try:
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost("localhost")
            sessionOptions.setServerPort(8194)
            
            self.session = blpapi.Session(sessionOptions)
            
            if not self.session.start():
                raise Exception("Failed to start Bloomberg session")
                
            if not self.session.openService("//blp/refdata"):
                raise Exception("Failed to open reference data service")
                
            self.service = self.session.getService("//blp/refdata")
            self.connected = True
            logger.info("Successfully connected to Bloomberg Terminal")
            
        except Exception as e:
            logger.error(f"Failed to connect to Bloomberg: {e}")
            self.connected = False
            raise
            
    def disconnect(self):
        """Disconnect from Bloomberg Terminal"""
        if self.session:
            self.session.stop()
            self.connected = False
            logger.info("Disconnected from Bloomberg Terminal")

# Global Bloomberg session
bloomberg = BloombergSession()

# Request/Response models
class NewsRequest(BaseModel):
    topics: List[str] = ["TOP", "FX", "ECONOMIC"]
    max_stories: int = 10
    hours_back: int = 24

class NewsStory(BaseModel):
    headline: str
    datetime: str
    story_id: str
    topics: List[str]
    synopsis: Optional[str] = None
    body: Optional[str] = None

class MarketDataRequest(BaseModel):
    securities: List[str]
    fields: List[str]

class MarketDataResponse(BaseModel):
    security: str
    fields: Dict[str, float]
    timestamp: str

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize Bloomberg connection on server start"""
    try:
        bloomberg.connect()
    except Exception as e:
        logger.error(f"Failed to initialize Bloomberg connection: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Bloomberg connection on server shutdown"""
    bloomberg.disconnect()

@app.get("/health")
async def health_check():
    """Check server and Bloomberg connection health"""
    return {
        "status": "healthy",
        "bloomberg_connected": bloomberg.connected,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/news", response_model=List[NewsStory])
async def get_bloomberg_news(request: NewsRequest):
    """Get Bloomberg news stories"""
    if not bloomberg.connected:
        raise HTTPException(status_code=503, detail="Bloomberg Terminal not connected")
    
    try:
        # Create news request
        news_request = bloomberg.service.createRequest("NewsDataRequest")
        
        # Set parameters
        for topic in request.topics:
            news_request.append("topics", f"N:{topic}")
        
        news_request.set("maxResults", request.max_stories)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=request.hours_back)
        
        news_request.set("startDateTime", start_date.strftime("%Y-%m-%dT%H:%M:%S"))
        news_request.set("endDateTime", end_date.strftime("%Y-%m-%dT%H:%M:%S"))
        
        # Send request
        bloomberg.session.sendRequest(news_request)
        
        # Collect stories
        stories = []
        while True:
            event = bloomberg.session.nextEvent(5000)  # 5 second timeout
            
            if event.eventType() == blpapi.Event.RESPONSE:
                for msg in event:
                    if msg.hasElement("data"):
                        data = msg.getElement("data")
                        for i in range(data.numValues()):
                            story_element = data.getValue(i)
                            
                            story = NewsStory(
                                headline=story_element.getElementAsString("headline"),
                                datetime=story_element.getElementAsString("dateTime"),
                                story_id=story_element.getElementAsString("storyId"),
                                topics=[],
                                synopsis=story_element.getElementAsString("synopsis") if story_element.hasElement("synopsis") else None
                            )
                            
                            # Get topics
                            if story_element.hasElement("topics"):
                                topics_element = story_element.getElement("topics")
                                for j in range(topics_element.numValues()):
                                    story.topics.append(topics_element.getValue(j))
                            
                            stories.append(story)
                break
                
            elif event.eventType() == blpapi.Event.TIMEOUT:
                break
        
        logger.info(f"Retrieved {len(stories)} news stories")
        return stories
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@app.post("/api/news/story/{story_id}")
async def get_news_story_detail(story_id: str):
    """Get full details of a specific news story"""
    if not bloomberg.connected:
        raise HTTPException(status_code=503, detail="Bloomberg Terminal not connected")
    
    try:
        # Create story request
        story_request = bloomberg.service.createRequest("StoryRequest")
        story_request.set("storyId", story_id)
        
        # Send request
        bloomberg.session.sendRequest(story_request)
        
        # Get response
        while True:
            event = bloomberg.session.nextEvent(5000)
            
            if event.eventType() == blpapi.Event.RESPONSE:
                for msg in event:
                    if msg.hasElement("story"):
                        story_data = msg.getElement("story")
                        return {
                            "story_id": story_id,
                            "headline": story_data.getElementAsString("headline"),
                            "body": story_data.getElementAsString("body"),
                            "datetime": story_data.getElementAsString("dateTime"),
                            "source": story_data.getElementAsString("source") if story_data.hasElement("source") else None,
                            "topics": []  # Parse topics if needed
                        }
                break
                
            elif event.eventType() == blpapi.Event.TIMEOUT:
                break
                
        raise HTTPException(status_code=404, detail="Story not found")
        
    except Exception as e:
        logger.error(f"Error fetching story: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching story: {str(e)}")

@app.post("/api/market-data", response_model=List[MarketDataResponse])
async def get_market_data(request: MarketDataRequest):
    """Get real-time market data"""
    if not bloomberg.connected:
        raise HTTPException(status_code=503, detail="Bloomberg Terminal not connected")
    
    try:
        # Create reference data request
        ref_request = bloomberg.service.createRequest("ReferenceDataRequest")
        
        # Add securities and fields
        for security in request.securities:
            ref_request.append("securities", security)
        
        for field in request.fields:
            ref_request.append("fields", field)
        
        # Send request
        bloomberg.session.sendRequest(ref_request)
        
        # Collect responses
        responses = []
        while True:
            event = bloomberg.session.nextEvent(5000)
            
            if event.eventType() == blpapi.Event.RESPONSE:
                for msg in event:
                    if msg.hasElement("securityData"):
                        security_data = msg.getElement("securityData")
                        
                        for i in range(security_data.numValues()):
                            security = security_data.getValue(i)
                            security_name = security.getElementAsString("security")
                            
                            field_data = {}
                            if security.hasElement("fieldData"):
                                fields = security.getElement("fieldData")
                                for field in request.fields:
                                    if fields.hasElement(field):
                                        field_data[field] = fields.getElement(field).getValue()
                            
                            responses.append(MarketDataResponse(
                                security=security_name,
                                fields=field_data,
                                timestamp=datetime.now().isoformat()
                            ))
                break
                
            elif event.eventType() == blpapi.Event.TIMEOUT:
                break
        
        return responses
        
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching market data: {str(e)}")

@app.get("/api/news/search")
async def search_news(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(20, description="Maximum number of results"),
    days_back: int = Query(7, description="Number of days to search back")
):
    """Search Bloomberg news"""
    if not bloomberg.connected:
        raise HTTPException(status_code=503, detail="Bloomberg Terminal not connected")
    
    try:
        # Create search request
        search_request = bloomberg.service.createRequest("NewsSearchRequest")
        search_request.set("query", query)
        search_request.set("maxResults", max_results)
        
        # Set date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        search_request.set("startDateTime", start_date.strftime("%Y-%m-%dT%H:%M:%S"))
        search_request.set("endDateTime", end_date.strftime("%Y-%m-%dT%H:%M:%S"))
        
        # Send request and process results
        bloomberg.session.sendRequest(search_request)
        
        results = []
        # Process response similar to get_bloomberg_news
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "search_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching news: {str(e)}")

@app.get("/api/fx/rates")
async def get_fx_rates(pairs: List[str] = Query(["EURUSD", "GBPUSD", "USDJPY"])):
    """Get current FX rates"""
    securities = [f"{pair} Curncy" for pair in pairs]
    fields = ["PX_LAST", "PX_BID", "PX_ASK", "LAST_UPDATE_DT"]
    
    request = MarketDataRequest(securities=securities, fields=fields)
    return await get_market_data(request)

if __name__ == "__main__":
    # Run server
    # For production, use: uvicorn bloomberg_api_server:app --host 0.0.0.0 --port 8080
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Listen on all interfaces
        port=8080,
        log_level="info"
    )