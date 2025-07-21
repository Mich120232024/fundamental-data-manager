# Bloomberg API Troubleshooting Guide

## 🚨 Critical Traps and Solutions

This guide documents all the traps we encountered during Bloomberg API development. **Read this BEFORE debugging API issues.**

---

## 1. 🔌 Bloomberg Terminal Connection Issues

### Problem: "Bloomberg API (blpapi) not installed"
**Trap**: API was hardcoded to fail with this message in stub connection
**Solution**: Implement real Bloomberg connection
```python
def start(self):
    """Start Bloomberg session - connects to localhost:8194"""
    try:
        import blpapi
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost('localhost')
        sessionOptions.setServerPort(8194)
        self.session = blpapi.Session(sessionOptions)
        if not self.session.start():
            raise Exception("Failed to start Bloomberg session")
```

### Problem: "Failed to start Bloomberg session"
**Debugging Steps**:
1. Check if Bloomberg Terminal is running on VM
2. Verify Terminal is logged in
3. Check if port 8194 is accessible
4. Restart Terminal if needed

### Problem: Connection works but returns no data
**Trap**: Bloomberg Terminal must be logged in with valid credentials
**Solution**: Ensure Terminal authentication is active

---

## 2. 🎯 Ticker Format Hell

### Problem: Wrong Risk Reversal Format
**Trap**: Used `EURUSD25RR1M` instead of `EURUSD25R1M`
**Solution**: Risk Reversals use single `R`: `{PAIR}{DELTA}R{TENOR} BGN Curncy`
**Example**: `EURUSD25R1M BGN Curncy` ✅ NOT `EURUSD25RR1M BGN Curncy` ❌

### Problem: Wrong Butterfly Format
**Trap**: Used `EURUSD25BF1M` instead of `EURUSD25B1M`
**Solution**: Butterflies use single `B`: `{PAIR}{DELTA}B{TENOR} BGN Curncy`
**Example**: `EURUSD25B1M BGN Curncy` ✅ NOT `EURUSD25BF1M BGN Curncy` ❌

### Problem: Missing Deltas in Testing
**Trap**: Only tested 10D and 25D, missing 5D, 15D, 35D
**Solution**: All deltas work - test systematically
**Validated Deltas**: 5D, 10D, 15D, 25D, 35D

### Problem: "Unknown/Invalid Security" errors
**Debugging Steps**:
1. Check ticker format matches Bloomberg conventions
2. Verify currency pair is 6 characters (EURUSD, GBPUSD)
3. Confirm tenor format (1M, 3M, 6M, 1Y)
4. Ensure `BGN Curncy` suffix is present

---

## 3. 💻 PowerShell Deployment Traps

### Problem: f-string syntax errors during deployment
**Trap**: PowerShell can't handle Python f-strings in heredocs
**Error**: `SyntaxError: f-string: unmatched '('`
**Solution**: Use string concatenation or .format() instead of f-strings

### Problem: String escaping issues
**Trap**: Complex string escaping in PowerShell commands
**Solution**: Use single quotes for outer strings, double quotes for inner
**Example**: 
```powershell
Invoke-Command -ScriptBlock {
    $pythonCode = 'print("Hello World")'
    python -c $pythonCode
}
```

### Problem: File encoding issues
**Trap**: PowerShell may change file encoding when writing Python files
**Solution**: Use `Set-Content` with `-Encoding UTF8` parameter

---

## 4. 🔍 API Response Handling Traps

### Problem: "'str' object has no attribute 'get'"
**Trap**: Bloomberg returns string errors instead of dictionaries
**Solution**: Check data type before calling .get()
```python
if isinstance(data, dict):
    value = data.get('PX_LAST')
else:
    error_message = str(data)
```

### Problem: Mixed success/error responses
**Trap**: Some securities succeed, others fail in batch requests
**Solution**: Handle each security individually in response array
```python
for security, data in bloomberg_data.items():
    if isinstance(data, dict):
        # Success case
        securities_data.append({
            'security': security,
            'fields': data,
            'success': True
        })
    else:
        # Error case
        securities_data.append({
            'security': security,
            'fields': {},
            'success': False,
            'error': str(data)
        })
```

---

## 5. 📊 Data Validation Traps

### Problem: Assuming only PX_LAST, PX_BID, PX_ASK exist
**Trap**: Missing other valuable fields like PX_HIGH, PX_LOW, PX_OPEN
**Solution**: Bloomberg provides complete intraday data
**Available Fields**: PX_LAST, PX_BID, PX_ASK, PX_HIGH, PX_LOW, PX_OPEN, CHG_PCT_1D, VOLUME

### Problem: No data validation on responses
**Trap**: Volatility values outside reasonable ranges
**Solution**: Add validation ranges (0-500% for volatility)

### Problem: Timestamp handling inconsistencies
**Trap**: Different date formats from Bloomberg
**Solution**: Standardize all timestamps to ISO format

---

## 6. 🚀 Deployment State Confusion

### Problem: "Production Ready" claims without deployment
**Trap**: Claimed success before actually deploying to VM
**Solution**: Always verify deployment with actual API calls

### Problem: Local vs VM code confusion
**Trap**: Working on local "toxic" code instead of VM implementation
**Solution**: Always work directly with VM code at `C:\BloombergAPI\main.py`

### Problem: Missing endpoints after deployment
**Trap**: Deployed partial code, missing volatility endpoints
**Solution**: Verify all endpoints exist after deployment
```bash
curl http://20.172.249.92:8080/health
curl -X POST http://20.172.249.92:8080/api/bloomberg/reference
```

---

## 7. 📝 Logging and Debugging Traps

### Problem: No logging for debugging
**Trap**: Errors occur but no trace of what happened
**Solution**: Comprehensive logging system implemented
**Log Files**:
- `api_requests.log` - All API requests
- `bloomberg_connection.log` - Bloomberg connection details
- `bloomberg_data.log` - Actual data responses
- `system_events.log` - System level events

### Problem: Log files not being written
**Debugging Steps**:
1. Check file permissions in `C:\BloombergAPI\logs\`
2. Verify logger initialization
3. Test with simple log write

### Problem: Log files too large
**Solution**: Implement log rotation
```python
handler = RotatingFileHandler('logs/api_requests.log', maxBytes=10*1024*1024, backupCount=5)
```

---

## 8. 🔐 Authentication and Security Traps

### Problem: Hardcoded API keys in code
**Trap**: Using `test` token directly in code
**Solution**: Environment variables for production
**Current**: Development uses `test` token
**Production**: Implement proper authentication

### Problem: No rate limiting
**Trap**: Overwhelming Bloomberg Terminal with requests
**Solution**: Implement 10 requests/second limit

---

## 9. 🌐 Network and Performance Traps

### Problem: Slow response times
**Trap**: Not optimizing batch requests
**Solution**: Combine multiple securities in single request
**Performance**: 
- Single security: 200-500ms
- Batch request: 1000-5000ms (more efficient than individual)

### Problem: Timeout issues
**Trap**: Default timeouts too short for Bloomberg
**Solution**: Appropriate timeouts by data type:
- Live data: 5000ms
- EOD data: 8000ms
- Historical data: 15000ms

### Problem: Connection pooling not implemented
**Trap**: Creating new Bloomberg connections for each request
**Solution**: Reuse Bloomberg Terminal connections

---

## 10. 📈 Data Type Specific Traps

### Problem: ATM Volatility missing bid/ask
**Trap**: Only requesting PX_LAST field
**Solution**: Request PX_BID and PX_ASK for complete spread data

### Problem: Risk Reversal negative values unexpected
**Trap**: Expecting only positive volatility values
**Solution**: Risk Reversals can be negative (call/put skew)

### Problem: Butterfly values too small
**Trap**: Expecting large butterfly values
**Solution**: Butterflies are typically small (0.1-2.0%)

---

## 🛠️ API Restart Procedures

### Problem: API server stops responding
**Debugging Steps**:
1. Check if process is running: `Get-Process python*`
2. Check port availability: `netstat -an | findstr :8080`
3. Check Bloomberg Terminal status
4. Restart API server

### Manual Restart Command:
```powershell
# Stop existing processes
Get-Process python* | Stop-Process -Force

# Start API server
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden
```

### Automated Restart Script:
```powershell
# Create restart_api.ps1
$process = Get-Process python* -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Name python* -Force
    Start-Sleep -Seconds 5
}
cd C:\BloombergAPI
Start-Process C:\Python311\python.exe -ArgumentList 'main.py' -WindowStyle Hidden
Write-Output "API server restarted"
```

---

## 🔍 Health Check Diagnostics

### Problem: Health check shows Bloomberg unavailable
**Debugging Steps**:
1. Check Bloomberg Terminal login status
2. Verify blpapi package installation: `pip show blpapi`
3. Test connection manually
4. Check Terminal API permissions

### Health Check Response Analysis:
```json
{
  "bloomberg_api_available": false,
  "bloomberg_terminal_running": false,
  "bloomberg_service_available": false,
  "bloomberg_error": "Failed to start Bloomberg session"
}
```

**Action**: Check Terminal status, restart if needed

---

## 📊 Log Analysis Patterns

### Problem: Finding relevant logs quickly
**Solution**: Use query_id to trace requests
**Pattern**: `grep "query_id_here" logs/*.log`

### Problem: Identifying Bloomberg connection issues
**Log Pattern**: Look for "session" or "connection" errors
**Files**: `bloomberg_connection.log`

### Problem: Data quality issues
**Log Pattern**: Look for "Unknown/Invalid Security" in `bloomberg_data.log`
**Action**: Check ticker format against validated patterns

---

## 🎯 Testing Best Practices

### Problem: Incomplete testing coverage
**Solution**: Test all components systematically
**Test Matrix**:
- ✅ All currency pairs (EURUSD, GBPUSD, USDJPY, etc.)
- ✅ All tenors (1W, 1M, 3M, 6M, 1Y, 2Y)
- ✅ All deltas (5D, 10D, 15D, 25D, 35D)
- ✅ All volatility types (ATM, RR, BF)

### Problem: Testing with mock data
**Solution**: Always use real Bloomberg data
**Validation**: Check response contains actual market values

### Problem: Not testing error conditions
**Solution**: Test invalid tickers, network failures, authentication errors

---

## 📋 Maintenance Checklist

### Daily Checks:
- [ ] Health check endpoint returns OK
- [ ] Bloomberg Terminal logged in
- [ ] Log files not too large
- [ ] API response times reasonable

### Weekly Checks:
- [ ] Test complete volatility surface
- [ ] Verify all ticker formats still work
- [ ] Check log rotation working
- [ ] Review error rates

### Monthly Checks:
- [ ] Update documentation
- [ ] Review performance metrics
- [ ] Check for new Bloomberg fields
- [ ] Validate security formats

---

## 🚨 Emergency Procedures

### Problem: Complete API failure
**Steps**:
1. Check VM accessibility: `ping 20.172.249.92`
2. Check API process: `Get-Process python*`
3. Check Bloomberg Terminal status
4. Restart everything if needed
5. Verify with health check

### Problem: Data quality issues
**Steps**:
1. Check recent logs for errors
2. Test with known good ticker
3. Compare with Bloomberg Terminal directly
4. Check if market is open
5. Verify field names are correct

### Problem: Performance degradation
**Steps**:
1. Check request volume in logs
2. Monitor response times
3. Check Bloomberg Terminal performance
4. Implement rate limiting if needed
5. Optimize batch requests

---

## 📞 Support Resources

### Bloomberg Terminal Issues:
- Check Terminal login status
- Verify API permissions
- Contact Bloomberg support if needed

### VM Access Issues:
- Check network connectivity
- Verify VM is running
- Check firewall settings

### API Development:
- Review this troubleshooting guide
- Check comprehensive logs
- Test with curl commands
- Use health check endpoint

---

## 🎯 Success Indicators

### API is working correctly when:
- ✅ Health check returns Bloomberg available
- ✅ Generic reference endpoint returns real data
- ✅ All ticker formats work (ATM, RR, BF)
- ✅ Bid/ask spreads are present
- ✅ Error handling is graceful
- ✅ Logs are being written
- ✅ Response times are reasonable

### Data quality is good when:
- ✅ Volatility values are in reasonable ranges (0-100%)
- ✅ Bid < Last < Ask for all securities
- ✅ Timestamps are recent (within 5 minutes for live data)
- ✅ No "Unknown/Invalid Security" errors for valid tickers
- ✅ All requested fields are returned

---

*Last Updated: July 16, 2025*  
*Status: Complete Troubleshooting Guide*  
*Coverage: All Known Traps and Solutions*