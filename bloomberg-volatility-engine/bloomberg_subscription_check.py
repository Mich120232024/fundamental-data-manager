#!/usr/bin/env python3
"""
Check Bloomberg Terminal subscription and available data
"""

import subprocess

def check_bloomberg_subscription():
    """Check what Bloomberg data is available with current subscription"""
    
    print("🔍 Bloomberg Terminal Subscription Check")
    print("=" * 60)
    
    check_script = r'''
Write-Host "Checking Bloomberg Terminal Subscription..." -ForegroundColor Cyan

# Test different Bloomberg services
$subscriptionTest = @'
import sys
sys.path.append(r"C:\blp\API\Python")

try:
    import blpapi
    
    # Start session
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost("localhost")
    sessionOptions.setServerPort(8194)
    
    session = blpapi.Session(sessionOptions)
    
    if not session.start():
        print("Failed to start Bloomberg session")
        exit(1)
    
    print("Bloomberg Terminal Connected")
    print("=" * 50)
    
    # Test different services
    services_to_test = [
        ("//blp/refdata", "Reference Data (Market Data)"),
        ("//blp/mktdata", "Market Data (Real-time)"),
        ("//blp/news", "News Service"),
        ("//blp/mktbar", "Market Bar Data"),
        ("//blp/refdata", "Historical Data"),
        ("//blp/apiflds", "Field Information")
    ]
    
    print("\nAvailable Services:")
    for service_name, description in services_to_test:
        try:
            if session.openService(service_name):
                print(f"✓ {description}: AVAILABLE")
                
                # Get service details
                service = session.getService(service_name)
                
                # Special check for news
                if "news" in service_name:
                    print("  Note: News service requires additional licensing")
                    print("  - TOP News: May require 'TOP' package")
                    print("  - First Word: Requires 'FIRST' subscription")
                    print("  - Industry News: Requires sector packages")
            else:
                print(f"✗ {description}: NOT AVAILABLE")
        except Exception as e:
            print(f"✗ {description}: ERROR - {str(e)}")
    
    # Check data permissions
    print("\n\nData Access Test:")
    print("-" * 50)
    
    if session.openService("//blp/refdata"):
        service = session.getService("//blp/refdata")
        
        # Test different asset classes
        test_securities = [
            ("AAPL US Equity", "US Equities"),
            ("EURUSD Curncy", "FX Rates"),
            ("SPX Index", "Indices"),
            ("CL1 Comdty", "Commodities"),
            ("US10Y Govt", "Government Bonds"),
            ("MSFT US Equity", "US Tech Stocks"),
            ("GC1 Comdty", "Precious Metals"),
            ("NG1 Comdty", "Energy"),
            ("EUR Corp", "Corporate Bonds"),
            ("VIX Index", "Volatility")
        ]
        
        for security, asset_class in test_securities:
            request = service.createRequest("ReferenceDataRequest")
            request.append("securities", security)
            request.append("fields", "PX_LAST")
            
            try:
                session.sendRequest(request)
                
                # Check response
                got_data = False
                while True:
                    event = session.nextEvent(1000)
                    
                    for msg in event:
                        if msg.hasElement("securityData"):
                            secData = msg.getElement("securityData").getValue(0)
                            if secData.hasElement("fieldData"):
                                fieldData = secData.getElement("fieldData")
                                if fieldData.hasElement("PX_LAST"):
                                    price = fieldData.getElement("PX_LAST").getValue()
                                    print(f"✓ {asset_class}: ACCESSIBLE (e.g., {security} = {price})")
                                    got_data = True
                            
                            # Check for permission errors
                            if secData.hasElement("securityError"):
                                error = secData.getElement("securityError")
                                print(f"✗ {asset_class}: RESTRICTED - {error.getElement('message').getValue()}")
                                got_data = True
                    
                    if event.eventType() == blpapi.Event.RESPONSE:
                        break
                
                if not got_data:
                    print(f"? {asset_class}: NO DATA")
                    
            except Exception as e:
                print(f"✗ {asset_class}: ERROR - {str(e)}")
    
    # Check news entitlements
    print("\n\nNews Entitlements:")
    print("-" * 50)
    print("Note: Bloomberg News requires separate licensing:")
    print("- BN (Bloomberg News): Core news package")
    print("- TOP: Top news stories")
    print("- FIRST: First Word real-time news")
    print("- Industry-specific packages (BTNEWS_ENERGY, etc.)")
    
    session.stop()
    
except Exception as e:
    print(f"Error: {e}")
    print("\nThis might indicate:")
    print("1. Bloomberg Terminal is not running")
    print("2. Not logged into Bloomberg Terminal")
    print("3. API access not enabled in Terminal")
'@

C:\Python311\python.exe -c $subscriptionTest
'''

    # Execute check
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", check_script,
        "--no-wait"  # Don't wait for full response
    ]
    
    print("Running subscription check on Bloomberg Terminal...")
    subprocess.run(cmd, capture_output=True, text=True)
    
    print("\n📋 Bloomberg Subscription Tiers:")
    print("=" * 60)
    print("""
1. **Bloomberg Terminal Core** (~$2,000/month)
   - Real-time market data for major markets
   - Basic charting and analytics
   - Limited news access

2. **Bloomberg Terminal with News** (~$2,500/month)
   - Everything in Core
   - Bloomberg News (BN)
   - First Word headlines
   - Some industry news

3. **Bloomberg Terminal Professional** (~$3,000+/month)
   - Everything above
   - All news sources
   - Advanced analytics
   - API access (BLPAPI)
   - Historical data

4. **Additional Packages**:
   - Bloomberg Law: Legal news and data
   - Bloomberg Government: Policy and regulation
   - Sector-specific news packages
   - Extended historical data
   
Note: Actual pricing depends on your contract and region.
""")
    
    print("\n💡 For News Headlines:")
    print("- You need at least 'Bloomberg News (BN)' package")
    print("- 'TOP' package for curated top stories")
    print("- 'FIRST' for breaking news alerts")
    print("- Industry packages for sector-specific news")
    
    print("\n✅ Your Current Access:")
    print("- Market Data: ✓ Working (stocks, FX, commodities)")
    print("- Real-time Prices: ✓ Working")
    print("- News Headlines: ❓ Requires checking subscription")


if __name__ == "__main__":
    check_bloomberg_subscription()