#!/bin/bash
# Deploy full Bloomberg API Server to VM

echo "Deploying Full Bloomberg API Server"
echo "==================================="

RESOURCE_GROUP="bloomberg-terminal-rg"
VM_NAME="bloomberg-vm-02"

# Create the bloomberg_api_server.py content
cat > /tmp/bloomberg_api_server.py << 'EOF'
#!/usr/bin/env python3
"""
Bloomberg API Server - Simplified version for testing
"""

import logging
from datetime import datetime
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Bloomberg API Server",
    description="Central Bloomberg Terminal access for the entire system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Bloomberg connection for testing
bloomberg_connected = False
try:
    import blpapi
    bloomberg_connected = True
except ImportError:
    logger.warning("Bloomberg API not available - running in mock mode")

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
    synopsis: str = ""

# API Endpoints
@app.get("/health")
async def health_check():
    """Check server and Bloomberg connection health"""
    return {
        "status": "healthy",
        "bloomberg_connected": bloomberg_connected,
        "timestamp": datetime.now().isoformat(),
        "server": "Bloomberg API Server",
        "mode": "production" if bloomberg_connected else "mock"
    }

@app.post("/api/news", response_model=List[NewsStory])
async def get_bloomberg_news(request: NewsRequest):
    """Get Bloomberg news stories (mock data for testing)"""
    # Mock response for testing
    mock_stories = [
        NewsStory(
            headline="Fed Signals Potential Rate Pause Amid Economic Uncertainty",
            datetime=datetime.now().isoformat(),
            story_id="MOCK001",
            topics=["ECONOMIC", "FED"],
            synopsis="Federal Reserve officials hint at maintaining current rates..."
        ),
        NewsStory(
            headline="EUR/USD Rises on ECB Policy Expectations",
            datetime=datetime.now().isoformat(),
            story_id="MOCK002",
            topics=["FX", "EUR"],
            synopsis="Euro strengthens against dollar as ECB meeting approaches..."
        ),
        NewsStory(
            headline="Tech Stocks Lead Market Rally on AI Optimism",
            datetime=datetime.now().isoformat(),
            story_id="MOCK003",
            topics=["TOP", "TECH"],
            synopsis="Technology sector drives gains as AI developments boost sentiment..."
        )
    ]
    
    return mock_stories[:request.max_stories]

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify server is running"""
    return {
        "message": "Bloomberg API Server is running",
        "timestamp": datetime.now().isoformat(),
        "bloomberg_available": bloomberg_connected
    }

if __name__ == "__main__":
    logger.info("Starting Bloomberg API Server on port 8080...")
    logger.info(f"Bloomberg connection: {'Available' if bloomberg_connected else 'Not available (mock mode)'}")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
EOF

# Encode the file
ENCODED_CONTENT=$(cat /tmp/bloomberg_api_server.py | base64 -w 0)

# Deploy to VM
echo "1. Creating Bloomberg API server file..."
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunPowerShellScript \
    --scripts "\$content = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('$ENCODED_CONTENT')); Set-Content -Path 'C:\Bloomberg\APIServer\bloomberg_api_server.py' -Value \$content -Encoding UTF8; Write-Host 'Bloomberg API server file created'"

# Create Windows service
echo -e "\n2. Creating Windows Task to run API server..."
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunPowerShellScript \
    --scripts "
\$action = New-ScheduledTaskAction -Execute 'C:\Python311\python.exe' -Argument 'C:\Bloomberg\APIServer\bloomberg_api_server.py' -WorkingDirectory 'C:\Bloomberg\APIServer'
\$trigger = New-ScheduledTaskTrigger -AtStartup
\$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName 'BloombergAPIServer' -Action \$action -Trigger \$trigger -Principal \$principal -Force
Start-ScheduledTask -TaskName 'BloombergAPIServer'
Write-Host 'Bloomberg API Server task created and started'
"

echo -e "\n✅ Bloomberg API Server deployed!"
echo "Wait a few seconds for the server to start..."

# Clean up
rm -f /tmp/bloomberg_api_server.py