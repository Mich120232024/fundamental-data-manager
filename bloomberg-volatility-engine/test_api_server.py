#!/usr/bin/env python3
"""
Simple Test API Server
Test server to verify network connectivity before deploying full Bloomberg server
"""

from fastapi import FastAPI
from datetime import datetime
import uvicorn

app = FastAPI(title="Test Bloomberg API Server")

@app.get("/")
async def root():
    return {"message": "Test Bloomberg API Server is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "server": "Test Bloomberg API Server",
        "timestamp": datetime.now().isoformat(),
        "bloomberg_connected": False,
        "note": "This is a test server without Bloomberg connection"
    }

@app.get("/test")
async def test_endpoint():
    return {
        "test": "successful",
        "server_time": datetime.now().isoformat(),
        "ready_for_bloomberg": True
    }

if __name__ == "__main__":
    print("Starting Test Bloomberg API Server on port 8080...")
    print("Access docs at: http://localhost:8080/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080)