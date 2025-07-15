#!/usr/bin/env python3
"""
Direct Bloomberg Terminal API test for FX volatility
"""

import subprocess

def test_fx_vol_direct():
    """Test FX volatility by calling Bloomberg API directly on the VM"""
    
    print("🎯 Testing FX Volatility via Direct Bloomberg API")
    print("=" * 60)
    
    # Simple direct test script
    test_script = r'''
# Test Bloomberg API directly
$testScript = @'
import sys
sys.path.append(r"C:\blp\API\Python")
import blpapi

# Connect to Bloomberg
sessionOptions = blpapi.SessionOptions()
sessionOptions.setServerHost("localhost")
sessionOptions.setServerPort(8194)
session = blpapi.Session(sessionOptions)

if not session.start():
    print("Failed to connect to Bloomberg Terminal")
    exit(1)

if not session.openService("//blp/refdata"):
    print("Failed to open service")
    exit(1)

service = session.getService("//blp/refdata")
print("Connected to Bloomberg Terminal")

# Test EURUSD with various volatility fields
request = service.createRequest("ReferenceDataRequest")
request.append("securities", "EURUSD Curncy")

# Add fields
fields = ["PX_LAST", "PX_BID", "PX_ASK", "VOLATILITY_30D", "VOLATILITY_90D", 
          "HIST_VOL_30D", "IMPLIED_VOL_1M", "1M_ATM_IMP_VOL"]

for field in fields:
    request.append("fields", field)

print("\nTesting EURUSD volatility fields:")
session.sendRequest(request)

while True:
    event = session.nextEvent(5000)
    for msg in event:
        if msg.hasElement("securityData"):
            secData = msg.getElement("securityData").getValue(0)
            if secData.hasElement("fieldData"):
                fieldData = secData.getElement("fieldData")
                print("\nAvailable fields:")
                for field in fields:
                    if fieldData.hasElement(field):
                        value = fieldData.getElement(field).getValue()
                        print(f"  {field}: {value}")
    
    if event.eventType() == blpapi.Event.RESPONSE:
        break

session.stop()
'@

Write-Host "Running direct Bloomberg API test..."
cd C:\
C:\Python311\python.exe -c $testScript
'''

    # Run the test
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", test_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Running direct Bloomberg API test on VM...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("Command timed out")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_fx_vol_direct()