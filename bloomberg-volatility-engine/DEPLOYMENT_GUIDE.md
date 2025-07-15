# 🚀 Bloomberg API Server Deployment Guide

## Quick Manual Deployment (5 minutes)

### Step 1: Connect to VM
```
RDP to: 20.172.249.92
Username: bloombergadmin  
Password: Ii89rra137+*
```

### Step 2: Open PowerShell as Administrator
Right-click PowerShell → Run as Administrator

### Step 3: Run this command block
Copy and paste this entire block into PowerShell:

```powershell
# Create directory and simple API server
$path = "C:\Bloomberg\APIServer"
New-Item -ItemType Directory -Force -Path $path
cd $path

# Create simple API server
@'
from fastapi import FastAPI
from datetime import datetime
import uvicorn

app = FastAPI(title="Bloomberg API Server")

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {"message": "Bloomberg API Server Running"}

uvicorn.run(app, host="0.0.0.0", port=8080)
'@ | Out-File -FilePath "api_server.py" -Encoding UTF8

# Install packages
C:\Python311\Scripts\pip.exe install fastapi uvicorn

# Open firewall
New-NetFirewallRule -DisplayName "API 8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow

# Start server
Start-Process python api_server.py
```

### Step 4: Verify It's Running
Open browser on VM and go to: http://localhost:8080/health

### Step 5: Test from Your Machine
From your local terminal:
```bash
curl http://20.172.249.92:8080/health
```

## Full Bloomberg Integration Deployment

Once the simple server works, deploy the full Bloomberg integration:

### 1. Copy these files to C:\Bloomberg\APIServer\
- bloomberg_api_server.py (the full version)
- bloomberg_client.py
- setup_bloomberg_service.ps1

### 2. Install Bloomberg packages
```powershell
pip install blpapi azure-identity azure-cosmos azure-eventhub
```

### 3. Run the full server
```powershell
python bloomberg_api_server.py
```

## Troubleshooting

### Can't connect from external?
1. Check Windows Firewall on VM
2. Check if server is running: `netstat -an | findstr 8080`
3. Check Task Manager for python.exe process

### Server crashes?
Run manually to see error:
```powershell
cd C:\Bloomberg\APIServer
python api_server.py
```

## Testing the API

Once running, test these endpoints:

### From VM:
- http://localhost:8080/docs - API documentation
- http://localhost:8080/health - Health check

### From your machine:
```python
import requests
response = requests.get("http://20.172.249.92:8080/health")
print(response.json())
```

## Files Summary

| File | Purpose | Location |
|------|---------|----------|
| quick_deploy.ps1 | One-click deployment script | Copy to VM |
| bloomberg_api_server.py | Full API server | C:\Bloomberg\APIServer\ |
| bloomberg_client.py | Client library | Your local machine |
| test_bloomberg_api.py | Test script | Your local machine |