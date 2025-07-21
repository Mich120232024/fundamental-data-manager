# Lessons Learned - Bloomberg Volatility Surface Project

## Critical Issues Encountered

### 1. Wrong API Running (2+ hours wasted)
- **Issue**: API was returning 404 for `/api/bloomberg/reference`
- **Root Cause**: Wrong Python script was running (`real_bloomberg_api.py` instead of `main_checkpoint_working_2025_07_16.py`)
- **Solution**: Restart with correct script
- **Lesson**: Always verify which API version is running when debugging

### 2. Substring Matching Bug (2+ hours wasted)
- **Issue**: 35D data was showing in 5D column
- **Root Cause**: `'35B1M'.includes('5B1M')` returns true
- **Solution**: Use regex pattern matching instead
- **Lesson**: Never use substring matching for structured data parsing

### 3. IP Whitelisting
- **Issue**: Error 0x204 when connecting to VM
- **Root Cause**: Dynamic IP changed
- **Solution**: Update NSG rules with new IP
- **Lesson**: Check IP first when connection fails

### 4. Service Control Endpoints Don't Exist
- **Issue**: "Bloomberg Disconnected" showing despite API running
- **Root Cause**: Frontend calling non-existent `/api/vm/service/status`
- **Solution**: Use health endpoint instead
- **Lesson**: Verify all endpoints exist before implementing UI features

### 5. Short-Dated Options (1D/2D/3D) Not Available
- **Issue**: User expected 1D/2D/3D tickers to work
- **Investigation**: Extensive testing showed these return "Unknown/Invalid Security"
- **Finding**: These tickers require specific Bloomberg subscriptions or don't exist for FX
- **Solution**: Use ON (overnight) as shortest tenor
- **Lesson**: Not all expected tickers exist; always test availability

### 6. Authentication Format Confusion
- **Issue**: Initial API calls returned "Not authenticated"
- **Root Cause**: Was using X-API-Key header instead of Bearer token
- **Solution**: Use `Authorization: Bearer test`
- **Lesson**: Check API documentation for exact auth format

### 7. Empty Tenor Rows
- **Issue**: Table showed many empty rows with no data
- **Root Cause**: Some tenors have no Bloomberg data
- **Solution**: Filter out rows where all values are null
- **Lesson**: Clean data presentation improves UX

## Best Practices Discovered

1. **Always Test Changes Immediately**
   - Don't assume fixes work
   - Verify with real API calls
   - Check console logs

2. **Use Proper Authentication**
   - Bearer token required: `Authorization: Bearer test`
   - Not just X-API-Key header

3. **Log Everything During Debugging**
   - Add console.log for API responses
   - Log parsed data transformations
   - Check actual vs expected values

4. **Understand Bloomberg Ticker Formats**
   - ON is special (no BGN for ATM)
   - Single letter for type (R not RR, B not BF)
   - Some tickers need specific subscriptions

5. **Test with Known Working Data First**
   - Always test with a known working ticker
   - Then test problematic tickers
   - Compare responses to identify issues

6. **Filter and Clean Data**
   - Remove empty rows for better visualization
   - Handle null values gracefully
   - Provide clear error messages

## Key Technical Decisions

1. **Regex Over Substring Matching**: More precise and avoids false matches
2. **Separate Live/Historical Methods**: Different endpoints have different requirements
3. **Client-Side Filtering**: Remove empty data after fetching for flexibility
4. **Comprehensive Error Logging**: Essential for debugging Bloomberg API issues

## Time Savers for Future

1. **Check these first when debugging**:
   - Is the correct API running?
   - Is your IP whitelisted?
   - Are you using the right auth header?
   - Test with curl before debugging React

2. **Bloomberg Ticker Quick Reference**:
   ```
   ATM: EURUSDV1M BGN Curncy (except ON: EURUSDVON Curncy)
   RR:  EURUSD25R1M BGN Curncy
   BF:  EURUSD25B1M BGN Curncy
   ```

3. **Common API Calls**:
   ```bash
   # Health check
   curl http://20.172.249.92:8080/health
   
   # Test ticker
   curl -X POST http://20.172.249.92:8080/api/bloomberg/reference \
     -H "Authorization: Bearer test" \
     -H "Content-Type: application/json" \
     -d '{"securities": ["EURUSD25R1M BGN Curncy"], "fields": ["PX_LAST"]}'
   ```