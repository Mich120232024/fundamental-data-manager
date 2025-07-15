#!/usr/bin/env python3
"""
Discover actual FX volatility fields available in Bloomberg
"""

import subprocess
import json

def discover_fx_volatility():
    """Run discovery on Bloomberg VM to find actual volatility fields"""
    
    print("🔍 Discovering FX Volatility Fields in Bloomberg")
    print("=" * 60)
    
    discovery_script = r'''
Write-Host "FX Volatility Field Discovery" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

$discovery = @'
import sys
sys.path.append(r"C:\blp\API\Python")
import blpapi
import json

print("\n1. CONNECTING TO BLOOMBERG")
print("-" * 40)

sessionOptions = blpapi.SessionOptions()
sessionOptions.setServerHost("localhost")
sessionOptions.setServerPort(8194)
session = blpapi.Session(sessionOptions)

if not session.start():
    print("Failed to connect")
    exit(1)

if not session.openService("//blp/refdata"):
    print("Failed to open service")
    exit(1)

service = session.getService("//blp/refdata")
print("✓ Connected to Bloomberg")

# Test currency pairs
currencies = ["EURUSD Curncy", "GBPUSD Curncy", "USDJPY Curncy"]

print("\n2. TESTING COMMON VOLATILITY FIELDS")
print("-" * 40)

# Common volatility field patterns to test
vol_fields_to_test = [
    # Historical volatility variations
    "HIST_VOLATILITY_10D", "HIST_VOLATILITY_20D", "HIST_VOLATILITY_30D",
    "HIST_VOL_10D", "HIST_VOL_20D", "HIST_VOL_30D", 
    "HISTORICAL_VOL_10D", "HISTORICAL_VOL_20D", "HISTORICAL_VOL_30D",
    "HV10", "HV20", "HV30", "HV60", "HV90",
    
    # Implied volatility variations
    "IMPVOL_1M", "IMPVOL_3M", "IMPVOL_6M",
    "IMP_VOL_1M", "IMP_VOL_3M", "IMP_VOL_6M",
    "IMPLIED_VOL_1M", "IMPLIED_VOL_3M",
    "IV1M", "IV3M", "IV6M",
    
    # ATM volatility
    "1M_IMPVOL_100DP", "3M_IMPVOL_100DP", 
    "1M_IMPVOL_100D_MID", "3M_IMPVOL_100D_MID",
    "1M_100_VOL", "3M_100_VOL",
    
    # Risk reversal and butterfly
    "1M_25DP_RR", "3M_25DP_RR", "6M_25DP_RR",
    "1M_25DP_BF", "3M_25DP_BF", "6M_25DP_BF",
    "1M_RR_25D", "3M_RR_25D",
    "1M_BF_25D", "3M_BF_25D",
    
    # Other vol metrics
    "VOLATILITY_INDEX", "VOL_INDEX",
    "REALIZED_VOLATILITY", "REAL_VOL_30D",
    "GARCH_VOL", "STOCH_VOL",
    
    # Simple volatility fields
    "VOLATILITY", "VOL", "HVOL", "IVOL"
]

# Test EURUSD first
test_security = "EURUSD Curncy"
found_fields = {}

for field in vol_fields_to_test:
    request = service.createRequest("ReferenceDataRequest")
    request.append("securities", test_security)
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
                            print(f"✓ Found: {field} = {value}")
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
                
    except:
        pass

print(f"\nFound {len(found_fields)} volatility fields")

# 3. Get field search/help
print("\n3. SEARCHING FIELD DEFINITIONS")
print("-" * 40)

# Try field search request
try:
    request = service.createRequest("FieldSearchRequest")
    request.set("searchSpec", "volatility")
    
    session.sendRequest(request)
    
    vol_related_fields = []
    while True:
        event = session.nextEvent(5000)
        
        for msg in event:
            if msg.hasElement("fieldData"):
                fieldDataArray = msg.getElement("fieldData")
                for i in range(fieldDataArray.numValues()):
                    fieldData = fieldDataArray.getValue(i)
                    if fieldData.hasElement("fieldId"):
                        field_id = fieldData.getElement("fieldId").getValue()
                        if "CURNCY" not in field_id.upper():  # Filter for currency-relevant
                            vol_related_fields.append(field_id)
        
        if event.eventType() == blpapi.Event.RESPONSE:
            break
    
    print(f"Found {len(vol_related_fields)} volatility-related fields")
    
    # Test some of the found fields on currencies
    print("\nTesting discovered fields on FX pairs:")
    for field in vol_related_fields[:20]:  # Test first 20
        request = service.createRequest("ReferenceDataRequest")
        request.append("securities", test_security)
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
                                print(f"  ✓ {field} = {value}")
                                found_fields[field] = value
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
                    
        except:
            pass
            
except Exception as e:
    print(f"Field search error: {e}")

# 4. Test FX option tickers for implied vol
print("\n4. TESTING FX OPTION TICKERS")
print("-" * 40)

# FX option tickers
fx_options = [
    "EUR1M Curncy",  # 1-month EURUSD ATM option
    "EUR3M Curncy",  # 3-month EURUSD ATM option
    "GBP1M Curncy",  # 1-month GBPUSD ATM option
    "JPY1M Curncy",  # 1-month USDJPY ATM option
]

option_fields = ["PX_LAST", "PX_MID", "BID", "ASK"]

for option in fx_options:
    request = service.createRequest("ReferenceDataRequest")
    request.append("securities", option)
    for field in option_fields:
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
                        values = {}
                        for field in option_fields:
                            if fieldData.hasElement(field):
                                values[field] = fieldData.getElement(field).getValue()
                        
                        if values:
                            print(f"\n{option}:")
                            for field, value in values.items():
                                print(f"  {field}: {value}")
                                
            if event.eventType() == blpapi.Event.RESPONSE:
                break
                
    except Exception as e:
        print(f"Error for {option}: {e}")

# Save results
results = {
    "found_volatility_fields": found_fields,
    "test_security": test_security,
    "field_count": len(found_fields)
}

with open(r"C:\Bloomberg\fx_volatility_fields.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Results saved to C:\\Bloomberg\\fx_volatility_fields.json")

session.stop()
'@

Write-Host "`nRunning FX volatility discovery..."
C:\Python311\python.exe -c $discovery

Write-Host "`n`nChecking results file..." -ForegroundColor Yellow
if (Test-Path "C:\Bloomberg\fx_volatility_fields.json") {
    $content = Get-Content "C:\Bloomberg\fx_volatility_fields.json" | ConvertFrom-Json
    Write-Host "Found $($content.field_count) volatility fields"
}

Write-Host "`nDiscovery complete!" -ForegroundColor Green
'''

    # Execute discovery
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", discovery_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Running FX volatility field discovery on Bloomberg Terminal...")
    print("This will test various field names to find what's available...\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ Discovery timed out but may have completed on VM")
    
    print("\n" + "=" * 60)
    print("Next step: Check C:\\Bloomberg\\fx_volatility_fields.json on the VM")
    print("This file contains all discovered volatility fields for FX")


if __name__ == "__main__":
    discover_fx_volatility()