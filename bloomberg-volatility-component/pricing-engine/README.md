# FX Options Pricing Engine

Python-based pricing engine for FX vanilla options, designed to work with the Bloomberg volatility surface frontend.

## Architecture Decision

We chose Python over JavaScript for the pricing engine because:
1. **NumPy/SciPy** provide fast, accurate numerical computation
2. **QuantLib-Python** is the industry standard for derivatives pricing
3. **Better precision** for complex mathematical calculations
4. **Easier validation** against academic papers and market standards
5. **Research collaboration** - RESEARCH_001 can directly validate Python implementations

## System Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│   React Frontend    │────▶│   FastAPI Backend   │────▶│ Pricing Engine   │
│  (Vite + TypeScript)│     │    (Python 3.11)    │     │ (QuantLib/Custom)│
└─────────────────────┘     └─────────────────────┘     └──────────────────┘
         Port 3501                  Port 8001                  In-process
            │                           │                           │
            │                           ▼                           │
            │                   ┌─────────────────┐                │
            └──────────────────▶│  Bloomberg API  │◀───────────────┘
                                │ (20.172.249.92) │
                                └─────────────────┘
```

## Getting Started

### Prerequisites
- Python 3.11+
- Poetry (recommended) or pip
- Access to Bloomberg API

### Installation

```bash
# Using Poetry (recommended)
cd pricing-engine
poetry install

# Using pip
pip install -r requirements.txt
```

### Running the Server

```bash
# Development
poetry run uvicorn main:app --reload --port 8001

# Production
poetry run uvicorn main:app --host 0.0.0.0 --port 8001
```

## API Endpoints

### Health Check
```
GET /health
```

### Market Data
```
POST /api/market-data/spot
{
  "pairs": ["EURUSD", "GBPUSD"]
}

POST /api/market-data/forward-points
{
  "pairs": ["EURUSD", "GBPUSD"],
  "tenors": ["1W", "1M", "3M"]
}

POST /api/market-data/rates
{
  "currencies": ["USD", "EUR"],
  "tenors": ["ON", "1W", "1M"]
}
```

### Options Pricing
```
POST /api/pricing/vanilla
{
  "pair": "EURUSD",
  "spot": 1.0900,
  "strike": 1.1000,
  "expiry": "1M",
  "option_type": "CALL",
  "notional": 1000000
}

POST /api/pricing/greeks
{
  "pair": "EURUSD",
  "spot": 1.0900,
  "strike": 1.1000,
  "expiry": "1M",
  "option_type": "CALL"
}
```

## Project Structure

```
pricing-engine/
├── api/              # FastAPI routes
│   ├── health.py     # Health check endpoints
│   ├── market_data.py # Bloomberg data integration
│   └── pricing.py    # Options pricing endpoints
├── core/             # Core pricing logic
│   ├── black_scholes.py  # Vanilla option pricing
│   ├── greeks.py     # Greeks calculations
│   └── volatility.py # Vol surface interpolation
├── models/           # Pydantic models
│   ├── market.py     # Market data models
│   └── options.py    # Options models
├── services/         # Business logic
│   ├── bloomberg.py  # Bloomberg API client
│   └── pricer.py     # Pricing service
└── tests/            # Unit tests
```

## Development

### Code Quality
```bash
# Format code
poetry run black .

# Lint
poetry run ruff .

# Run tests
poetry run pytest
```

### Adding Dependencies
```bash
poetry add package-name
```

## Collaboration

- **Frontend Integration**: SOFTWARE_MANAGER
- **Quantitative Research**: RESEARCH_001
- **Bloomberg Data**: Existing API at http://20.172.249.92:8080