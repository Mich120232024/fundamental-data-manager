K DATA EVER"""
    query_id = f"fx_vol_live_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    logger.info(f"FX volatility request: {request.currency_pairs} x {request.tenors} | Query ID: {query_id}")
    
    try:
        # Build Bloomberg securities for volatility surface
        securities = []
        for pair in request.currency_pairs:
            for tenor in request.tenors:
                securities.append(f"{pair}{tenor} ATM Vol")
                securities.append(f"{pair}{tenor} 25D RR")
                securities.append(f"{pair}{tenor} 25D BF")
                securities.append(f"{pair}{tenor} 10D RR")
                securities.append(f"{pair}{tenor} 10D BF")
        
        fields = ["VOLATILITY_MID", "C25R", "C25B", "C10R", "C10B"]
        
        # Get REAL data from Bloomberg Terminal - will fail until Bloomberg is connected
        bloomberg_data = bloomberg.get_reference_data(securities, fields)
        
        # This code will only execute if Bloomberg is working
        volatility_data = []
        for security, data in bloomberg_data.items():
            volatility_data.append({
                "security": security,
                "VOLATILITY_MID": data.get("VOLATILITY_MID"),
                "C25R": data.get("C25R"),
                "C25B": data.get("C25B"),
                "C10R": data.get("C10R"),
                "C10B": data.get("C10B")
            })
        
        return {
            "success": True,
            "data": {
                "data_type": "live_fx_volatility",
                "timestamp": datetime.now().isoformat(),
                "currency_pairs": request.currency_pairs,
                "tenors": request.tenors,
                "vol_types": ["ATM_VOL", "25D_RR", "25D_BF", "10D_RR", "10D_BF"],
                "raw_data": volatility_data,
                "source": "Bloomberg Terminal - LIVE DATA"
            },
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "query_id": query_id,
        }
        
    except Exception as e:
        logger.error(f"FX volatility error: {e} | Query ID: {query_id}")
        raise HTTPException(status_code=503, detail="Bloomberg Terminal not available - NO MOCK DATA PROVIDED")

# ==========================================
# APPLICATION STARTUP
# ==========================================


# Generic Bloomberg Reference Data Endpoint
class BloombergReferenceRequest(BaseModel):
    securities: List[str]
    fields: List[str]

@app.post('/api/bloomberg/reference')
async def get_bloomberg_reference_data(request: BloombergReferenceRequest, api_key: str = Depends(validate_api_key)):
    query_id = f'reference_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    
    try:
        bloomberg_data = bloomberg.get_reference_data(request.securities, request.fields)
        
        securities_data = []
        for security, data in bloomberg_data.items():
            if isinstance(data, dict):
                securities_data.append({
                    'security': security,
                    'fields': data,
                    'success': True
                })
            else:
                securities_data.append({
                    'security': security,
                    'fields': {},
                    'success': False,
                    'error': str(data)
                })
        
        return {
            'success': True,
            'data': {
                'securities_data': securities_data,
                'source': 'Bloomberg Terminal'
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
if __name__ == "__main__":
    logger.info("Starting Bloomberg FX Volatility API Server - REAL DATA ONLY")
    logger.info("ZERO TOLERANCE FOR MOCK DATA - Will show no data until Bloomberg Terminal is connected")
    
    # Start server on all interfaces
    uvicorn.run(
        app,
        host="0.0.0.0",  # Bind to all network interfaces
        port=8080,
        log_level="info",
        access_log=True
    )



