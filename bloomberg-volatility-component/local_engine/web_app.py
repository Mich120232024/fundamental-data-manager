"""
Web application for displaying Bloomberg-style volatility surface
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'api'))

from multi_tenor_client import MultiTenorVolatilityClient
import json

app = FastAPI()

# Set up templates
templates = Jinja2Templates(directory="templates")

# Initialize client
vol_client = MultiTenorVolatilityClient()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/volatility/{currency_pair}")
async def get_volatility_surface(currency_pair: str):
    """Get volatility surface data for a currency pair"""
    
    # Get multi-tenor surface
    df = vol_client.get_multi_tenor_surface(currency_pair)
    
    # Create both matrices
    bloomberg_matrix = vol_client.create_bloomberg_style_matrix(df)
    full_matrix = vol_client.create_full_delta_matrix(df)
    
    # Convert to JSON-friendly format
    result = {
        "currency_pair": currency_pair,
        "bloomberg_style": bloomberg_matrix.to_dict(orient="records"),
        "full_delta": full_matrix.to_dict(orient="records"),
        "success_count": df[df["success"] == True].shape[0],
        "failed_count": df[df["success"] == False].shape[0],
        "failures": df[df["success"] == False][["tenor", "error"]].to_dict(orient="records") if df[df["success"] == False].shape[0] > 0 else []
    }
    
    return result


@app.get("/api/volatility/{currency_pair}/{tenor}")
async def get_single_tenor(currency_pair: str, tenor: str):
    """Get detailed volatility data for a single tenor"""
    
    result = vol_client.get_tenor_surface(currency_pair, tenor)
    
    if result["success"]:
        # Convert DataFrame to dict for JSON response
        result["full_data"] = result["full_data"].to_dict(orient="records")
    
    return result


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    print("Starting Bloomberg Volatility Surface Web App...")
    print("Open http://localhost:8000 in your browser")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)