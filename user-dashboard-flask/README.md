# Flask Dashboard (Port 5001) - Packaged Version

## Overview
This is the standalone Flask-based dashboard server extracted from the user-management-dashboard project. It serves on port 5001 with a Flask proxy style architecture.

## Directory Structure
```
user-dashboard-flask-port5001/
├── backend/
│   ├── app.py                 # Main Flask application
│   └── cosmos_db_manager.py   # Database manager
├── frontend/                  # Static assets and HTML files
├── static/                    # Flask static files
├── templates/                 # Flask templates
├── requirements.txt           # Python dependencies
├── start_dashboard.sh         # Startup script
└── test_dashboard_server.py   # Test script
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   # Copy .env from parent Research & Analytics Services directory
   # Ensure COSMOS_ENDPOINT and COSMOS_KEY are set
   ```

3. **Start the server:**
   ```bash
   cd backend
   python app.py
   ```
   OR
   ```bash
   ./start_dashboard.sh
   ```

4. **Test the server:**
   ```bash
   python test_dashboard_server.py
   ```

## Access
- **URL:** http://localhost:5001
- **Style:** Flask proxy architecture with inline JavaScript
- **Features:** Cosmos DB integration, message composition, formatted display

## Key Characteristics
- All JavaScript embedded directly in HTML (inline approach)
- Flask-based backend with CORS support
- Cosmos DB integration for message management
- Professional styling with Cytoscape.js for graph visualization

## Dependencies
- Flask + Flask-CORS
- Azure Cosmos DB SDK
- Python-dotenv for environment variables
- See requirements.txt for complete list

## Notes
This package preserves the original Flask architecture style that was working on port 5001 before consolidation efforts.