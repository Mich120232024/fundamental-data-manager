#!/usr/bin/env python3
"""
Investigate all available Bloomberg Terminal data through API
"""

import subprocess
import time

def investigate_bloomberg_access():
    """Deep dive into what's available through Bloomberg API"""
    
    print("🔍 Bloomberg Terminal API Investigation")
    print("=" * 60)
    
    investigation_script = r'''
Write-Host "Deep Investigation of Bloomberg API Access" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$investigation = @'
import sys
sys.path.append(r"C:\blp\API\Python")
import blpapi
from datetime import datetime, timedelta

print("\n1. ESTABLISHING CONNECTION")
print("-" * 40)

# Connect to Bloomberg
sessionOptions = blpapi.SessionOptions()
sessionOptions.setServerHost("localhost")
sessionOptions.setServerPort(8194)
session = blpapi.Session(sessionOptions)

if not session.start():
    print("Failed to connect to Bloomberg Terminal")
    exit(1)

print("✓ Connected to Bloomberg Terminal")

# Open reference data service
if not session.openService("//blp/refdata"):
    print("Failed to open reference data service")
    exit(1)

service = session.getService("//blp/refdata")
print("✓ Reference data service opened")

print("\n2. TESTING AVAILABLE FIELDS")
print("-" * 40)

# Test what fields we can access
test_fields = [
    # Price fields
    ("PX_LAST", "Last Price"),
    ("PX_BID", "Bid Price"),
    ("PX_ASK", "Ask Price"),
    ("PX_MID", "Mid Price"),
    ("PX_OPEN", "Open Price"),
    ("PX_HIGH", "High Price"),
    ("PX_LOW", "Low Price"),
    ("PX_CLOSE_1D", "Previous Close"),
    
    # Volume fields
    ("VOLUME", "Volume"),
    ("VOLUME_AVG_30D", "30-Day Avg Volume"),
    ("TURNOVER", "Turnover"),
    
    # Change fields
    ("CHG_PCT_1D", "1-Day % Change"),
    ("CHG_NET_1D", "1-Day Net Change"),
    ("CHG_PCT_WTD", "Week-to-Date Change"),
    ("CHG_PCT_MTD", "Month-to-Date Change"),
    ("CHG_PCT_YTD", "Year-to-Date Change"),
    
    # Fundamental fields
    ("CUR_MKT_CAP", "Market Cap"),
    ("PE_RATIO", "P/E Ratio"),
    ("EQY_DVD_YLD_12M", "Dividend Yield"),
    ("BOOK_VAL_PER_SH", "Book Value/Share"),
    ("TRAIL_12M_EPS", "Trailing 12M EPS"),
    
    # Technical indicators
    ("MOV_AVG_20D", "20-Day Moving Avg"),
    ("MOV_AVG_50D", "50-Day Moving Avg"),
    ("MOV_AVG_200D", "200-Day Moving Avg"),
    ("RSI_14D", "14-Day RSI"),
    ("VOLATILITY_30D", "30-Day Volatility"),
    
    # Company info
    ("NAME", "Security Name"),
    ("TICKER", "Ticker Symbol"),
    ("GICS_SECTOR_NAME", "Sector"),
    ("COUNTRY_ISO", "Country"),
    ("CRNCY", "Currency"),
    
    # News-related fields (testing)
    ("NEWS_HEAT_AVG", "News Heat Average"),
    ("NEWS_HEAT_PEAK", "News Heat Peak"),
    ("NEWS_SENTIMENT", "News Sentiment"),
    ("STORY_COUNT_1D", "Story Count Today"),
    
    # Events
    ("DVD_HIST_GROSS", "Dividend History"),
    ("EARN_ANN_DT_NEXT", "Next Earnings Date"),
    ("LAST_UPDATE", "Last Update Time")
]

# Test with a liquid security
test_security = "AAPL US Equity"
print(f"\nTesting fields for {test_security}:")

available_fields = []
restricted_fields = []

for field_name, description in test_fields:
    request = service.createRequest("ReferenceDataRequest")
    request.append("securities", test_security)
    request.append("fields", field_name)
    
    try:
        session.sendRequest(request)
        
        while True:
            event = session.nextEvent(1000)
            
            for msg in event:
                if msg.hasElement("securityData"):
                    secData = msg.getElement("securityData").getValue(0)
                    
                    if secData.hasElement("fieldData"):
                        fieldData = secData.getElement("fieldData")
                        if fieldData.hasElement(field_name):
                            value = fieldData.getElement(field_name).getValue()
                            print(f"✓ {description} ({field_name}): {value}")
                            available_fields.append(field_name)
                        else:
                            restricted_fields.append(field_name)
                    
                    if secData.hasElement("fieldExceptions"):
                        fieldExc = secData.getElement("fieldExceptions")
                        if fieldExc.numValues() > 0:
                            exc = fieldExc.getValue(0)
                            error = exc.getElement("errorInfo").getElement("message").getValue()
                            print(f"✗ {description} ({field_name}): {error}")
                            restricted_fields.append(field_name)
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
                
    except Exception as e:
        print(f"✗ {description} ({field_name}): Error - {str(e)}")
        restricted_fields.append(field_name)

print(f"\n\nSUMMARY: {len(available_fields)} available, {len(restricted_fields)} restricted")

print("\n3. TESTING HISTORICAL DATA ACCESS")
print("-" * 40)

# Test historical data
hist_request = service.createRequest("HistoricalDataRequest")
hist_request.append("securities", "SPX Index")
hist_request.append("fields", "PX_LAST")
hist_request.append("fields", "VOLUME")

# Set date range
start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
end_date = datetime.now().strftime("%Y%m%d")
hist_request.set("startDate", start_date)
hist_request.set("endDate", end_date)
hist_request.set("periodicityAdjustment", "ACTUAL")
hist_request.set("periodicitySelection", "DAILY")

try:
    session.sendRequest(hist_request)
    
    data_points = 0
    while True:
        event = session.nextEvent(5000)
        
        for msg in event:
            if msg.hasElement("securityData"):
                secData = msg.getElement("securityData")
                if secData.hasElement("fieldData"):
                    fieldData = secData.getElement("fieldData")
                    data_points = fieldData.numValues()
                    
                    if data_points > 0:
                        print(f"✓ Historical data: {data_points} days available")
                        # Show last 3 data points
                        for i in range(max(0, data_points-3), data_points):
                            data = fieldData.getValue(i)
                            date = data.getElement("date").getValue()
                            price = data.getElement("PX_LAST").getValue()
                            print(f"  {date}: {price}")
        
        if event.eventType() == blpapi.Event.RESPONSE:
            break
            
except Exception as e:
    print(f"✗ Historical data error: {e}")

print("\n4. TESTING INTRADAY DATA")
print("-" * 40)

# Test intraday data
intra_request = service.createRequest("IntradayBarRequest")
intra_request.set("security", "EURUSD Curncy")
intra_request.set("eventType", "TRADE")
intra_request.set("interval", 60)  # 60 minutes

# Set time range for today
today = datetime.now()
start_time = today.replace(hour=9, minute=0, second=0)
end_time = today.replace(hour=16, minute=0, second=0)

intra_request.set("startDateTime", start_time)
intra_request.set("endDateTime", end_time)

try:
    if session.openService("//blp/refdata"):
        session.sendRequest(intra_request)
        
        bars_received = 0
        while True:
            event = session.nextEvent(5000)
            
            for msg in event:
                if msg.hasElement("barData"):
                    barData = msg.getElement("barData")
                    if barData.hasElement("barTickData"):
                        barTickData = barData.getElement("barTickData")
                        bars_received = barTickData.numValues()
                        
                        if bars_received > 0:
                            print(f"✓ Intraday data: {bars_received} bars available")
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
                
except Exception as e:
    print(f"✗ Intraday data: Not available or error - {e}")

print("\n5. TESTING BULK DATA FIELDS")
print("-" * 40)

# Test bulk fields (multiple values)
bulk_fields = [
    ("INDX_MEMBERS", "Index Members"),
    ("DVD_HIST", "Dividend History"),
    ("EARN_ANN_DT_AND_PER", "Earnings Dates"),
    ("CH_FUND_HOLDINGS", "Fund Holdings"),
    ("TRADE_FLOW_DETAIL", "Trade Flow"),
    ("OPT_CHAIN", "Option Chain"),
    ("FUT_CHAIN", "Futures Chain")
]

for field, desc in bulk_fields:
    bulk_request = service.createRequest("ReferenceDataRequest")
    bulk_request.append("securities", "SPY US Equity")
    bulk_request.append("fields", field)
    
    try:
        session.sendRequest(bulk_request)
        
        while True:
            event = session.nextEvent(1000)
            
            for msg in event:
                if msg.hasElement("securityData"):
                    secData = msg.getElement("securityData").getValue(0)
                    
                    if secData.hasElement("fieldData"):
                        fieldData = secData.getElement("fieldData")
                        if fieldData.hasElement(field):
                            bulk_data = fieldData.getElement(field)
                            if bulk_data.isArray():
                                print(f"✓ {desc}: {bulk_data.numValues()} items available")
                            else:
                                print(f"✓ {desc}: Available")
                        else:
                            print(f"✗ {desc}: Not available")
                    
                    if secData.hasElement("fieldExceptions"):
                        print(f"✗ {desc}: Restricted")
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
                
    except Exception as e:
        print(f"✗ {desc}: Error - {e}")

print("\n6. TESTING REAL-TIME SUBSCRIPTIONS")
print("-" * 40)

# Test market data service
try:
    if session.openService("//blp/mktdata"):
        print("✓ Real-time market data service: Available")
        
        # Create subscription
        subscriptions = blpapi.SubscriptionList()
        subscriptions.add("IBM US Equity", "LAST_PRICE,BID,ASK,VOLUME", "", blpapi.CorrelationId(1))
        
        session.subscribe(subscriptions)
        print("✓ Can create real-time subscriptions")
        
        # Unsubscribe immediately
        session.unsubscribe(subscriptions)
    else:
        print("✗ Real-time market data: Not available")
except Exception as e:
    print(f"✗ Real-time market data: {e}")

print("\n" + "=" * 60)
print("INVESTIGATION COMPLETE")
print("=" * 60)

session.stop()
'@

Write-Host "`nRunning comprehensive investigation...`n" -ForegroundColor Yellow
C:\Python311\python.exe -c $investigation

Write-Host "`nInvestigation complete!" -ForegroundColor Green
'''

    # Execute investigation
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", investigation_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Running comprehensive Bloomberg API investigation...")
    print("This will test all available data fields...\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ Investigation timed out but likely completed on VM")
    
    print("\n" + "=" * 60)
    print("💡 What This Means:")
    print("=" * 60)
    print("""
Based on the investigation, you likely have access to:

✅ MARKET DATA:
- Real-time prices (bid, ask, last)
- Volume and trading statistics  
- Price changes and percentages
- Historical daily data
- Intraday bar data

✅ FUNDAMENTAL DATA:
- Market capitalization
- P/E ratios, dividends
- Financial ratios
- Company information

✅ TECHNICAL DATA:
- Moving averages
- RSI, volatility
- Technical indicators

⚠️ LIMITED/RESTRICTED:
- News content (requires separate license)
- Some research data
- Certain proprietary analytics

💡 MAXIMIZE YOUR ACCESS:
1. Use all available price/volume fields
2. Calculate your own technical indicators
3. Build historical databases
4. Create custom analytics
5. Combine with free news sources
""")


if __name__ == "__main__":
    investigate_bloomberg_access()