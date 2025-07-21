# Deployment Scripts

This folder contains scripts used to deploy and maintain the Bloomberg API on the Azure VM.

## Active Scripts (Still Relevant)

### 1. `deploy_working_version.ps1`
- **Purpose**: Deploys the complete working Bloomberg API with all endpoints
- **Status**: CURRENT - This is the latest working deployment
- **Use when**: Need to restore API to fully working state

### 2. `deploy_historical_safely.ps1`
- **Purpose**: Adds historical data functionality to existing API
- **Status**: TESTED - Successfully adds historical endpoint
- **Use when**: Need to add historical data capability

### 3. `deploy_fixed_logging.ps1`
- **Purpose**: Fixes logging for the reference endpoint
- **Status**: APPLIED - Logging now works correctly
- **Use when**: If logging issues arise

## Archive Folder

The `archive/` folder contains scripts from the development process that are no longer needed:
- Various ticker format fixes (we found the correct format)
- Multiple attempts at endpoint deployment
- Debugging and troubleshooting scripts
- Intermediate fixes that were superseded

## VM Connection Info

- **VM**: bloomberg-vm-02
- **IP**: 20.172.249.92
- **Port**: 8080
- **Main file**: C:\BloombergAPI\main.py
- **Logs**: C:\BloombergAPI\logs\

## Current API Status

All endpoints working:
- GET /health
- POST /api/fx/rates/live
- POST /api/bloomberg/reference
- POST /api/bloomberg/historical