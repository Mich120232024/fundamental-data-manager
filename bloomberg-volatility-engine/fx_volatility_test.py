#!/usr/bin/env python3
"""
FX Volatility Test - Run this directly on the Bloomberg VM
Copy this file to the VM and run: python fx_volatility_test.py
"""

import sys
sys.path.append(r"C:\blp\API\Python")
import blpapi
from datetime import datetime, timedelta
import math

def test_fx_volatility():
    """Test what FX volatility data is available in Bloomberg"""
    
    print("=" * 60)
    print("FX VOLATILITY DATA TEST")
    print("=" * 60)
    
    # Connect to Bloomberg
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost("localhost")
    sessionOptions.setServerPort(8194)
    session = blpapi.Session(sessionOptions)
    
    if not session.start():
        print("ERROR: Cannot connect to Bloomberg Terminal")
        print("Make sure Terminal is running and logged in")
        return
    
    if not session.openService("//blp/refdata"):
        print("ERROR: Cannot open reference data service")
        return
    
    service = session.getService("//blp/refdata")
    print("✓ Connected to Bloomberg Terminal\n")
    
    # Test FX pairs
    fx_pairs = ["EURUSD Curncy", "GBPUSD Curncy", "USDJPY Curncy"]
    
    print("1. TESTING VOLATILITY FIELDS")
    print("-" * 40)
    
    # All possible volatility field names to test
    volatility_fields = [
        # ATM Implied Volatility
        "1M_ATM_IMP_VOL", "3M_ATM_IMP_VOL", "6M_ATM_IMP_VOL",
        "1M_IMPVOL_100DP", "3M_IMPVOL_100DP", 
        "EUR1M_100_VOL", "EUR3M_100_VOL",
        
        # Generic volatility
        "VOLATILITY_30D", "VOLATILITY_90D", "VOLATILITY_180D",
        "HIST_VOL_30D", "HISTORICAL_VOL_30D",
        "REALIZED_VOL_30D", "IVOL_MID",
        
        # Risk Reversal and Butterfly
        "1M_25DP_RR", "3M_25DP_RR",
        "1M_25DP_BF", "3M_25DP_BF",
        "25D_RR_1M", "25D_BF_1M",
        
        # Simple fields
        "VOLATILITY", "IMPLIED_VOL", "HIST_VOL"
    ]
    
    found_fields = {}
    
    for pair in fx_pairs[:1]:  # Test with EURUSD first
        print(f"\nTesting {pair}:")
        
        for field in volatility_fields:
            request = service.createRequest("ReferenceDataRequest")
            request.append("securities", pair)
            request.append("fields", field)
            
            try:
                session.sendRequest(request)
                
                while True:
                    event = session.nextEvent(1000)
                    
                    for msg in event:
                        if msg.hasElement("securityData"):
                            secData = msg.getElement("securityData").getValue(0)
                            
                            if secData.hasElement("fieldData"):
                                fieldData = secData.getElement("fieldData")
                                if fieldData.hasElement(field):
                                    value = fieldData.getElement(field).getValue()
                                    found_fields[field] = value
                                    print(f"  ✓ {field} = {value}")
                    
                    if event.eventType() == blpapi.Event.RESPONSE:
                        break
            except:
                pass
    
    if not found_fields:
        print("  No volatility fields found with those names")
    
    print("\n\n2. TESTING FX OPTION TICKERS")
    print("-" * 40)
    
    # FX option tickers that might give implied vol
    option_tickers = [
        "EUR1M Curncy",  # 1-month EUR vol
        "EUR3M Curncy",  # 3-month EUR vol
        "EURUSDV1M Index",  # EUR/USD 1M volatility
        "EURUSDV3M Index",  # EUR/USD 3M volatility
    ]
    
    for ticker in option_tickers:
        request = service.createRequest("ReferenceDataRequest")
        request.append("securities", ticker)
        request.append("fields", "PX_LAST")
        request.append("fields", "SECURITY_DES")
        
        try:
            session.sendRequest(request)
            
            while True:
                event = session.nextEvent(1000)
                
                for msg in event:
                    if msg.hasElement("securityData"):
                        secData = msg.getElement("securityData").getValue(0)
                        
                        if secData.hasElement("fieldData"):
                            fieldData = secData.getElement("fieldData")
                            if fieldData.hasElement("PX_LAST"):
                                px = fieldData.getElement("PX_LAST").getValue()
                                desc = fieldData.getElement("SECURITY_DES").getValue() if fieldData.hasElement("SECURITY_DES") else ""
                                print(f"✓ {ticker}: {px} ({desc})")
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
        except:
            print(f"✗ {ticker}: Not found")
    
    print("\n\n3. CALCULATING HISTORICAL VOLATILITY")
    print("-" * 40)
    
    # Get historical prices to calculate volatility
    hist_request = service.createRequest("HistoricalDataRequest")
    hist_request.append("securities", "EURUSD Curncy")
    hist_request.append("fields", "PX_LAST")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    hist_request.set("startDate", start_date.strftime("%Y%m%d"))
    hist_request.set("endDate", end_date.strftime("%Y%m%d"))
    hist_request.set("periodicitySelection", "DAILY")
    
    session.sendRequest(hist_request)
    
    prices = []
    
    while True:
        event = session.nextEvent(5000)
        
        for msg in event:
            if msg.hasElement("securityData"):
                secData = msg.getElement("securityData")
                if secData.hasElement("fieldData"):
                    fieldData = secData.getElement("fieldData")
                    
                    for i in range(fieldData.numValues()):
                        data = fieldData.getValue(i)
                        price = data.getElement("PX_LAST").getValue()
                        prices.append(float(price))
        
        if event.eventType() == blpapi.Event.RESPONSE:
            break
    
    if len(prices) > 1:
        # Calculate returns
        returns = []
        for i in range(1, len(prices)):
            ret = math.log(prices[i] / prices[i-1])
            returns.append(ret)
        
        # Calculate volatility
        mean_ret = sum(returns) / len(returns)
        variance = sum((r - mean_ret) ** 2 for r in returns) / (len(returns) - 1)
        daily_vol = math.sqrt(variance)
        annual_vol = daily_vol * math.sqrt(252) * 100
        
        print(f"EURUSD Historical Volatility (30 days):")
        print(f"  Daily vol: {daily_vol * 100:.3f}%")
        print(f"  Annualized vol: {annual_vol:.2f}%")
        print(f"  Data points: {len(prices)}")
    
    print("\n\n4. CURRENT FX RATES")
    print("-" * 40)
    
    # Get current rates
    for pair in fx_pairs:
        request = service.createRequest("ReferenceDataRequest")
        request.append("securities", pair)
        request.append("fields", "PX_LAST")
        request.append("fields", "PX_HIGH")
        request.append("fields", "PX_LOW")
        
        session.sendRequest(request)
        
        while True:
            event = session.nextEvent(1000)
            
            for msg in event:
                if msg.hasElement("securityData"):
                    secData = msg.getElement("securityData").getValue(0)
                    
                    if secData.hasElement("fieldData"):
                        fieldData = secData.getElement("fieldData")
                        last = fieldData.getElement("PX_LAST").getValue() if fieldData.hasElement("PX_LAST") else "N/A"
                        high = fieldData.getElement("PX_HIGH").getValue() if fieldData.hasElement("PX_HIGH") else "N/A"
                        low = fieldData.getElement("PX_LOW").getValue() if fieldData.hasElement("PX_LOW") else "N/A"
                        
                        print(f"\n{pair}:")
                        print(f"  Last: {last}")
                        print(f"  Range: {low} - {high}")
                        
                        if isinstance(last, (int, float)) and isinstance(high, (int, float)) and isinstance(low, (int, float)):
                            range_pct = ((high - low) / last) * 100
                            print(f"  Daily range: {range_pct:.3f}%")
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
    
    session.stop()
    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    test_fx_volatility()