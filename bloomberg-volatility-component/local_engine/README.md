# Local Engine - Bloomberg Volatility Analysis

This directory contains the **LOCAL** code that consumes the Bloomberg API running on the VM.
It is completely separate from the VM API code.

## Directory Structure

```
local_engine/
├── README.md              # This file
├── src/                   # Source code
│   ├── api/              # API client to connect to Bloomberg VM
│   ├── data/             # Data processing and transformation
│   ├── components/       # UI components (React/Vue/etc)
│   └── utils/            # Utility functions
├── tests/                # Unit and integration tests
└── examples/             # Example usage scripts
```

## Key Principles

1. **NO VM CODE HERE** - This is purely client-side code
2. **API URL**: http://20.172.249.92:8080
3. **Authentication**: Bearer token "test" (development)
4. **Purpose**: Analyze and render Bloomberg data locally

## Getting Started

See `src/api/bloomberg_client.py` for the API client implementation.