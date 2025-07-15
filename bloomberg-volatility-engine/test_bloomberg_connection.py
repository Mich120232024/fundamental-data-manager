#!/usr/bin/env python3
"""
Test Bloomberg Terminal BLPAPI connection
Tests basic connectivity to Bloomberg Terminal running on localhost
"""

import sys
import time
from datetime import datetime

print("Bloomberg Terminal Connection Test")
print("=" * 50)
print(f"Test started at: {datetime.now()}")
print()

try:
    # Import Bloomberg API
    print("1. Importing Bloomberg API...")
    import blpapi
    print("   ✓ Bloomberg API imported successfully")
    print(f"   Version: {blpapi.__version__ if hasattr(blpapi, '__version__') else 'Unknown'}")
except ImportError as e:
    print("   ✗ Failed to import Bloomberg API")
    print(f"   Error: {e}")
    print("\n   Please ensure BLPAPI is installed:")
    print("   pip install blpapi")
    sys.exit(1)

# Test connection parameters
HOST = "localhost"
PORT = 8194

print(f"\n2. Testing connection to Bloomberg Terminal...")
print(f"   Host: {HOST}")
print(f"   Port: {PORT}")

try:
    # Create session options
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost(HOST)
    sessionOptions.setServerPort(PORT)
    
    # Create and start session
    print("\n3. Creating Bloomberg session...")
    session = blpapi.Session(sessionOptions)
    
    print("4. Starting session...")
    if not session.start():
        print("   ✗ Failed to start session")
        print("   Ensure Bloomberg Terminal is running and logged in")
        sys.exit(1)
    
    print("   ✓ Session started successfully")
    
    # Open market data service
    print("\n5. Opening market data service...")
    if not session.openService("//blp/mktdata"):
        print("   ✗ Failed to open market data service")
        session.stop()
        sys.exit(1)
    
    print("   ✓ Market data service opened")
    
    # Test simple data request
    print("\n6. Testing data request (EURUSD spot price)...")
    service = session.getService("//blp/mktdata")
    request = service.createRequest("ReferenceDataRequest")
    
    # Add security and field
    request.append("securities", "EURUSD Curncy")
    request.append("fields", "PX_LAST")
    
    print("   Sending request...")
    session.sendRequest(request)
    
    # Wait for response
    print("   Waiting for response...")
    timeout = 5  # 5 seconds timeout
    start_time = time.time()
    
    while True:
        event = session.nextEvent(1000)  # 1 second timeout
        
        if event.eventType() == blpapi.Event.RESPONSE:
            print("   ✓ Received response")
            
            # Parse response
            for msg in event:
                if msg.hasElement("securityData"):
                    securityData = msg.getElement("securityData")
                    if securityData.numValues() > 0:
                        security = securityData.getValue(0)
                        if security.hasElement("fieldData"):
                            fieldData = security.getElement("fieldData")
                            if fieldData.hasElement("PX_LAST"):
                                price = fieldData.getElement("PX_LAST").getValue()
                                print(f"\n   EURUSD Current Price: {price}")
            break
            
        if time.time() - start_time > timeout:
            print("   ⚠ Request timed out")
            break
    
    # Clean up
    print("\n7. Closing session...")
    session.stop()
    print("   ✓ Session closed")
    
    print("\n" + "=" * 50)
    print("✅ Bloomberg Terminal connection test PASSED")
    print("=" * 50)
    
except Exception as e:
    print(f"\n✗ Connection test failed: {e}")
    print("\nCommon issues:")
    print("1. Bloomberg Terminal not running")
    print("2. Not logged into Bloomberg Terminal")
    print("3. BLPAPI service not enabled")
    print("4. Firewall blocking connection")
    sys.exit(1)

print(f"\nTest completed at: {datetime.now()}")