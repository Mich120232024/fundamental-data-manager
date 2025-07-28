# Fundamental Data Manager

Production-ready visualization and management system for economic data APIs.

## Quick Start

### Backend (Port 8850)
```bash
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your COSMOS_KEY

python main.py
```

### Frontend (Port 3850)
```bash
cd frontend
npm install
npm run dev
```

## Features

- 📊 **Real-time API Catalog**: Live data from Cosmos DB (no mocks)
- 🎨 **Bloomberg-style UI**: Professional GZC theme
- 📈 **Statistics Dashboard**: API, endpoint, dataset, and field counts
- 🔄 **Live Updates**: Real-time synchronization

## Tech Stack

- **Backend**: FastAPI + Azure Cosmos DB
- **Frontend**: React + TypeScript + Vite
- **Styling**: Bloomberg component theme system

## Data Source

Connects to `data-collection-db.api_catalog` with real economic data APIs:
- FRED, Eurostat, CFTC, World Bank, Bank of Japan, etc.

## Ports

- Frontend: http://localhost:3850
- Backend API: http://localhost:8850