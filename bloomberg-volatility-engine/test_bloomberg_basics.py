#!/usr/bin/env python3
"""
Test basic Bloomberg capabilities - what can we actually access?
"""

import subprocess

def test_bloomberg_basics():
    """Test basic Bloomberg Terminal capabilities"""
    
    print("🧪 Testing Basic Bloomberg Capabilities")
    print("=" * 60)
    
    test_script = r'''
Write-Host "Testing Bloomberg Terminal Basic Capabilities" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Test 1: Basic Bloomberg Connection
$test1 = @'
import sys
sys.path.append(r"C:\blp\API\Python")

print("\n1. TESTING BASIC CONNECTION")
print("-" * 40)

try:
    import blpapi
    print("✓ Bloomberg API module loaded")
    
    # Create session
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost("localhost")
    sessionOptions.setServerPort(8194)
    
    session = blpapi.Session(sessionOptions)
    if session.start():
        print("✓ Connected to Bloomberg Terminal")
        
        # List available services
        if session.openService("//blp/refdata"):
            print("✓ Reference Data Service available")
        
        session.stop()
    else:
        print("✗ Cannot connect to Bloomberg Terminal")
        print("  Make sure Terminal is running and logged in")
        
except Exception as e:
    print(f"✗ Error: {e}")
'@

Write-Host "`nTest 1: Basic Connection Test"
C:\Python311\python.exe -c $test1

# Test 2: Check what news-related fields we can access
$test2 = @'
import sys
sys.path.append(r"C:\blp\API\Python")
import blpapi

print("\n2. TESTING NEWS-RELATED FIELDS")
print("-" * 40)

try:
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost("localhost")
    sessionOptions.setServerPort(8194)
    session = blpapi.Session(sessionOptions)
    
    if session.start() and session.openService("//blp/refdata"):
        service = session.getService("//blp/refdata")
        
        # Test news-related fields
        request = service.createRequest("ReferenceDataRequest")
        request.append("securities", "AAPL US Equity")
        
        # Try different news-related fields
        news_fields = [
            "NEWS_HEAT_AVG_DAILY",
            "NEWS_SENTIMENT_DAILY_AVG", 
            "STORY_COUNT_LAST_ONE_DAY",
            "NEWS_HEAT_READ_DAILY",
            "NEWS_HEAT_COMMENT_DAILY"
        ]
        
        for field in news_fields:
            request.append("fields", field)
        
        print("Testing news-related fields for AAPL:")
        session.sendRequest(request)
        
        while True:
            event = session.nextEvent(5000)
            
            for msg in event:
                if msg.hasElement("securityData"):
                    secData = msg.getElement("securityData").getValue(0)
                    
                    if secData.hasElement("fieldData"):
                        fieldData = secData.getElement("fieldData")
                        
                        for field in news_fields:
                            if fieldData.hasElement(field):
                                value = fieldData.getElement(field).getValue()
                                print(f"  ✓ {field}: {value}")
                            else:
                                print(f"  ✗ {field}: Not available")
                    
                    if secData.hasElement("fieldExceptions"):
                        fieldExc = secData.getElement("fieldExceptions")
                        for i in range(fieldExc.numValues()):
                            exc = fieldExc.getValue(i)
                            field = exc.getElement("fieldId").getValue()
                            error = exc.getElement("errorInfo").getElement("message").getValue()
                            print(f"  ✗ {field}: {error}")
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
        
        session.stop()
        
except Exception as e:
    print(f"Error: {e}")
'@

Write-Host "`nTest 2: News-Related Fields Test"
C:\Python311\python.exe -c $test2

# Test 3: Check if we can access MSG function
$test3 = @'
import sys
sys.path.append(r"C:\blp\API\Python")
import blpapi

print("\n3. TESTING MSG FUNCTION ACCESS")
print("-" * 40)

try:
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost("localhost")
    sessionOptions.setServerPort(8194)
    session = blpapi.Session(sessionOptions)
    
    if session.start() and session.openService("//blp/refdata"):
        service = session.getService("//blp/refdata")
        
        # Try to access MSG function (this is how Terminal accesses messages/news)
        request = service.createRequest("ReferenceDataRequest")
        
        # MSG function syntax: /msgn/[number] or /msgt/[ticker]
        request.append("securities", "/msgn/1")  # Try message number 1
        request.append("fields", "MSG_HEADER")
        request.append("fields", "MSG_BODY")
        
        print("Testing MSG function access:")
        session.sendRequest(request)
        
        while True:
            event = session.nextEvent(5000)
            
            for msg in event:
                if msg.hasElement("securityData"):
                    print("  ✓ MSG function might be accessible")
                elif msg.messageType() == "ResponseError":
                    print("  ✗ MSG function not accessible via API")
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
        
        session.stop()
        
except Exception as e:
    print(f"Error: {e}")
'@

Write-Host "`nTest 3: MSG Function Test"
C:\Python311\python.exe -c $test3

# Test 4: Check what's in the Terminal's local storage
$test4 = @'
import os
import glob

print("\n4. CHECKING BLOOMBERG LOCAL FILES")
print("-" * 40)

# Common Bloomberg directories
bloomberg_paths = [
    r"C:\blp\data",
    r"C:\Bloomberg",
    r"C:\Users\bloombergadmin\AppData\Local\Bloomberg",
    r"C:\ProgramData\Bloomberg"
]

for path in bloomberg_paths:
    if os.path.exists(path):
        print(f"\n✓ Found: {path}")
        # List some files (not all, just to see what's there)
        try:
            files = glob.glob(os.path.join(path, "*"))[:5]
            for f in files:
                print(f"  - {os.path.basename(f)}")
        except:
            print("  (Cannot list contents)")
    else:
        print(f"✗ Not found: {path}")
'@

Write-Host "`nTest 4: Bloomberg Local Files Check"
C:\Python311\python.exe -c $test4

Write-Host "`n`nBasic tests complete!" -ForegroundColor Green
'''

    # Execute tests
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", test_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Running basic Bloomberg tests on VM...")
    print("This will check what we can actually access...\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ Tests timed out but may have completed")
    
    print("\n" + "=" * 60)
    print("💡 Based on these tests, we'll know:")
    print("1. If Bloomberg Terminal is running")
    print("2. What news-related data we can access")
    print("3. If MSG functions work")
    print("4. What local files might contain news")
    print("\nThen we can design the best workflow!")


if __name__ == "__main__":
    test_bloomberg_basics()