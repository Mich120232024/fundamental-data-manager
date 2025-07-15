#!/usr/bin/env python3
"""
Direct FX volatility exploration on Bloomberg Terminal
"""

import subprocess

def explore_fx_volatility_direct():
    """Run FX volatility exploration directly on the VM"""
    
    print("🎯 Direct FX Volatility Exploration on Bloomberg Terminal")
    print("=" * 60)
    
    direct_script = r'''
Write-Host "FX Volatility Direct Exploration" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Create and run the exploration script
$fxVolScript = @'
import sys
sys.path.append(r"C:\blp\API\Python")
import blpapi
from datetime import datetime, timedelta
import json

print("\nConnecting to Bloomberg Terminal...")

# Create session
sessionOptions = blpapi.SessionOptions()
sessionOptions.setServerHost("localhost")
sessionOptions.setServerPort(8194)
session = blpapi.Session(sessionOptions)

if not session.start():
    print("Failed to connect to Bloomberg Terminal")
    exit(1)

if not session.openService("//blp/refdata"):
    print("Failed to open reference data service")
    exit(1)

service = session.getService("//blp/refdata")
print("✓ Connected to Bloomberg Terminal")

# Test FX pairs
fx_pairs = ["EURUSD Curncy", "GBPUSD Curncy", "USDJPY Curncy", "AUDUSD Curncy"]

print("\n1. CURRENT FX RATES & VOLATILITY METRICS")
print("-" * 50)

# Basic fields that should work
basic_fields = [
    "PX_LAST", "PX_BID", "PX_ASK", 
    "PX_HIGH", "PX_LOW", "PX_OPEN",
    "CHG_PCT_1D", "VOLUME"
]

# Volatility fields to test
vol_fields = [
    # Historical volatility variations
    "VOLATILITY_10D", "VOLATILITY_20D", "VOLATILITY_30D",
    "VOLATILITY_60D", "VOLATILITY_90D", "VOLATILITY_180D",
    "HIST_VOL_10D", "HIST_VOL_20D", "HIST_VOL_30D",
    "REALIZED_VOL_10D", "REALIZED_VOL_20D", "REALIZED_VOL_30D",
    
    # Implied volatility
    "IMPLIED_VOLATILITY", "IMPVOL_MID",
    "1M_IMPVOL", "3M_IMPVOL", "6M_IMPVOL",
    "1M_ATM_IMP_VOL", "3M_ATM_IMP_VOL",
    
    # Options data
    "OPT_IMPLIED_VOLATILITY_MID",
    "IVOL_DELTA_NEUTRAL",
    
    # Risk reversal and butterfly
    "RISK_REVERSAL_25D_1M", "BUTTERFLY_25D_1M",
    "25_DELTA_RISK_REVERSAL", "25_DELTA_BUTTERFLY"
]

for pair in fx_pairs:
    print(f"\n{pair}:")
    
    # Get basic data first
    request = service.createRequest("ReferenceDataRequest")
    request.append("securities", pair)
    for field in basic_fields:
        request.append("fields", field)
    
    session.sendRequest(request)
    
    basic_data = {}
    while True:
        event = session.nextEvent(5000)
        for msg in event:
            if msg.hasElement("securityData"):
                secData = msg.getElement("securityData").getValue(0)
                if secData.hasElement("fieldData"):
                    fieldData = secData.getElement("fieldData")
                    for field in basic_fields:
                        if fieldData.hasElement(field):
                            basic_data[field] = fieldData.getElement(field).getValue()
        
        if event.eventType() == blpapi.Event.RESPONSE:
            break
    
    # Display basic data
    if basic_data:
        print(f"  Spot: {basic_data.get('PX_LAST', 'N/A')}")
        print(f"  Bid/Ask: {basic_data.get('PX_BID', 'N/A')} / {basic_data.get('PX_ASK', 'N/A')}")
        print(f"  Today Range: {basic_data.get('PX_LOW', 'N/A')} - {basic_data.get('PX_HIGH', 'N/A')}")
        print(f"  Change: {basic_data.get('CHG_PCT_1D', 'N/A')}%")
        
        # Calculate range-based volatility
        if all(k in basic_data for k in ['PX_HIGH', 'PX_LOW', 'PX_LAST']):
            range_vol = ((basic_data['PX_HIGH'] - basic_data['PX_LOW']) / basic_data['PX_LAST']) * 100
            print(f"  Daily Range Vol: {range_vol:.3f}%")
    
    # Test volatility fields
    print("  Testing volatility fields...")
    found_vol_fields = {}
    
    for vol_field in vol_fields:
        request = service.createRequest("ReferenceDataRequest")
        request.append("securities", pair)
        request.append("fields", vol_field)
        
        try:
            session.sendRequest(request)
            
            while True:
                event = session.nextEvent(1000)
                for msg in event:
                    if msg.hasElement("securityData"):
                        secData = msg.getElement("securityData").getValue(0)
                        if secData.hasElement("fieldData"):
                            fieldData = secData.getElement("fieldData")
                            if fieldData.hasElement(vol_field):
                                value = fieldData.getElement(vol_field).getValue()
                                found_vol_fields[vol_field] = value
                                print(f"    ✓ {vol_field}: {value}")
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
        except:
            pass
    
    if not found_vol_fields:
        print("    No direct volatility fields available")

print("\n\n2. TESTING FX VOLATILITY INDICES")
print("-" * 50)

# Test volatility index securities
vol_indices = [
    "EURUSDV1M Index", "EURUSDV3M Index", "EURUSDV6M Index",
    "GBPUSDV1M Index", "USDJPYV1M Index",
    "EUR1M Curncy", "EUR3M Curncy", "EUR6M Curncy",
    "CVIX Index", "EUVIX Index", "BPVIX Index"
]

for vol_index in vol_indices:
    request = service.createRequest("ReferenceDataRequest")
    request.append("securities", vol_index)
    request.append("fields", "PX_LAST")
    request.append("fields", "SECURITY_NAME")
    
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
                            name = fieldData.getElement("SECURITY_NAME").getValue() if fieldData.hasElement("SECURITY_NAME") else vol_index
                            print(f"✓ {vol_index}: {px} ({name})")
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
    except:
        pass

print("\n\n3. HISTORICAL DATA FOR VOLATILITY CALCULATION")
print("-" * 50)

# Get historical data for EURUSD
hist_request = service.createRequest("HistoricalDataRequest")
hist_request.append("securities", "EURUSD Curncy")
hist_request.append("fields", "PX_LAST")

# Last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

hist_request.set("startDate", start_date.strftime("%Y%m%d"))
hist_request.set("endDate", end_date.strftime("%Y%m%d"))
hist_request.set("periodicitySelection", "DAILY")

session.sendRequest(hist_request)

prices = []
dates = []

while True:
    event = session.nextEvent(5000)
    for msg in event:
        if msg.hasElement("securityData"):
            secData = msg.getElement("securityData")
            if secData.hasElement("fieldData"):
                fieldData = secData.getElement("fieldData")
                for i in range(fieldData.numValues()):
                    data = fieldData.getValue(i)
                    date = data.getElement("date").getValue()
                    price = data.getElement("PX_LAST").getValue()
                    dates.append(date)
                    prices.append(price)
    
    if event.eventType() == blpapi.Event.RESPONSE:
        break

if len(prices) > 1:
    print(f"✓ Retrieved {len(prices)} days of historical data")
    print(f"  Latest: {prices[-1]} on {dates[-1]}")
    print(f"  Oldest: {prices[0]} on {dates[0]}")
    
    # Calculate simple historical volatility
    import math
    returns = []
    for i in range(1, len(prices)):
        ret = math.log(prices[i] / prices[i-1])
        returns.append(ret)
    
    # Standard deviation of returns
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
    daily_vol = math.sqrt(variance)
    
    # Annualize (252 trading days)
    annual_vol = daily_vol * math.sqrt(252) * 100
    
    print(f"\n  Calculated Historical Volatility:")
    print(f"  Daily Vol: {daily_vol * 100:.3f}%")
    print(f"  Annualized Vol: {annual_vol:.2f}%")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "fx_pairs_tested": fx_pairs,
    "volatility_indices_tested": vol_indices,
    "historical_data_points": len(prices) if 'prices' in locals() else 0,
    "calculated_volatility": annual_vol if 'annual_vol' in locals() else None
}

with open(r"C:\Bloomberg\fx_volatility_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✓ Results saved to C:\\Bloomberg\\fx_volatility_results.json")

session.stop()
print("\nExploration complete!")
'@

# Save and run the script
$scriptPath = "C:\Bloomberg\fx_volatility_direct.py"
$fxVolScript | Out-File -FilePath $scriptPath -Encoding UTF8

Write-Host "`nRunning FX volatility exploration..."
C:\Python311\python.exe $scriptPath

Write-Host "`nChecking results file..."
if (Test-Path "C:\Bloomberg\fx_volatility_results.json") {
    Write-Host "`nResults:" -ForegroundColor Green
    Get-Content "C:\Bloomberg\fx_volatility_results.json"
}

Write-Host "`nDone!" -ForegroundColor Green
'''

    # Execute on VM
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", direct_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Running FX volatility exploration directly on Bloomberg Terminal...")
    print("This will test all available volatility fields and calculate historical vol...\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("Command timed out but exploration may still be running...")
    
    print("\n" + "=" * 60)
    print("Check C:\\Bloomberg\\fx_volatility_results.json on the VM for full results!")


if __name__ == "__main__":
    explore_fx_volatility_direct()