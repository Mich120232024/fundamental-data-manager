# Frontend Debugging Guide for Cosmos DB Viewer

## Overview
This guide covers debugging the Cosmos DB viewer frontend issues, particularly when containers or documents aren't loading properly.

## Browser Developer Tools Setup

### Safari Developer Tools
1. **Enable Safari Developer Tools:**
   - Open Safari → Preferences → Advanced
   - Check "Show Develop menu in menu bar"
   - Or use `⌘ + ⌥ + I` to open Web Inspector

2. **Key Panels for Debugging:**
   - **Console**: View JavaScript errors and debug logs
   - **Network**: Monitor API requests and responses
   - **Elements**: Inspect HTML/CSS and DOM changes
   - **Sources**: Debug JavaScript with breakpoints

### Chrome/Edge Developer Tools
1. **Open Developer Tools:**
   - Right-click → "Inspect"
   - Press `F12`
   - Use `⌘ + ⌥ + I` (Mac) or `Ctrl + Shift + I` (Windows)

## Debug Version Features

The debug version (`cosmos_db_viewer_debug.html`) includes:

### 1. Debug Console Panel
- **Location**: Bottom of the page with dark background
- **Features**:
  - Real-time logging of all API calls
  - Network request timing
  - Error messages with detailed stack traces
  - Connection status indicator
  - Clear log button

### 2. Enhanced Error Display
- **Error Details**: Shows full error messages with technical details
- **API Response Logging**: Logs partial API responses for inspection
- **Connection Status**: Visual indicator showing API connectivity

### 3. Extensive Console Logging
All debug messages are logged to both the debug panel and browser console with categories:
- **INFO**: General information (blue)
- **SUCCESS**: Successful operations (green)
- **ERROR**: Errors and failures (red)
- **NETWORK**: API requests and responses (orange)

## Common Issues and Solutions

### 1. Containers Not Loading

**Symptoms:**
- Empty sidebar or "Loading containers..." stuck
- "Failed to load containers" error

**Debug Steps:**
1. Check debug panel for network errors
2. Look for API connectivity issues
3. Verify server is running on correct port

**Browser Dev Tools:**
```javascript
// In Console tab, check if API is accessible:
fetch('/api/containers')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

**Network Tab:**
- Look for `/api/containers` request
- Check status code (should be 200)
- Examine response body for error messages

### 2. Documents Not Loading

**Symptoms:**
- Container loads but shows "No documents found"
- Documents API returns errors

**Debug Steps:**
1. Select a container and check debug panel
2. Look for document API request failures
3. Check if container ID is being passed correctly

**Browser Dev Tools:**
```javascript
// Test specific container:
fetch('/api/containers/messages/documents?limit=10')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

### 3. JavaScript Errors

**Debug Steps:**
1. Open Console tab for JavaScript errors
2. Check for syntax errors or undefined variables
3. Look for promise rejections

**Common Error Patterns:**
- `TypeError: Cannot read property 'id' of undefined`
- `ReferenceError: API_BASE is not defined`
- Network errors: `Failed to fetch`

### 4. Authentication/Connection Issues

**Symptoms:**
- 401/403 errors in Network tab
- Connection status shows "Connection Error"

**Debug Steps:**
1. Check if Cosmos DB credentials are properly configured
2. Verify `.env` file is loaded correctly
3. Check server logs for authentication errors

## Manual Testing Commands

### Test API Endpoints Directly

1. **Check Server Status:**
```bash
curl http://localhost:5001/api/stats
```

2. **List Containers:**
```bash
curl http://localhost:5001/api/containers
```

3. **Get Documents:**
```bash
curl "http://localhost:5001/api/containers/messages/documents?limit=5"
```

### Browser Console Commands

1. **Check API Base:**
```javascript
console.log('API Base:', window.location.origin);
```

2. **Test Fetch Function:**
```javascript
// Test the debug fetch wrapper
fetchWithDebug('/api/stats')
  .then(r => r.json())
  .then(console.log);
```

3. **Check Current State:**
```javascript
console.log('Containers:', allContainers);
console.log('Documents:', allDocuments);
console.log('Current Container:', currentContainer);
```

## Network Request Monitoring

### Using Network Tab
1. Open Network tab before loading page
2. Filter by "XHR" or "Fetch" to see API calls
3. Click on requests to see:
   - Request headers
   - Response headers
   - Response body
   - Timing information

### Key Requests to Monitor
- `GET /api/stats` - Initial connectivity test
- `GET /api/containers` - Container list
- `GET /api/containers/{id}/documents` - Document list

## Performance Debugging

### Timing Analysis
The debug version shows request timing:
- Look for slow API calls (>1000ms)
- Check for timeout errors
- Monitor concurrent request handling

### Memory Usage
- Check for memory leaks in large document lists
- Monitor DOM element creation/destruction
- Watch for excessive logging

## Error Recovery

### Automatic Retry Logic
```javascript
// The debug version includes retry logic for failed requests
// Check debug panel for retry attempts
```

### Manual Recovery
```javascript
// Force reload containers
loadContainers();

// Force reload documents
loadDocuments(currentContainer);

// Clear and reinitialize
location.reload();
```

## Advanced Debugging

### Setting Breakpoints
1. Open Sources tab
2. Find the JavaScript code
3. Click line numbers to set breakpoints
4. Trigger the action to hit breakpoint

### Console Debugging
```javascript
// Enable verbose logging
DEBUG.log('Custom debug message', 'info');

// Check fetch wrapper
console.log(fetchWithDebug.toString());

// Inspect current DOM state
console.log(document.getElementById('containerList').innerHTML);
```

## Production vs Debug Mode

### Debug Mode Benefits:
- Extensive logging
- Error details
- Network monitoring
- Connection status
- Performance timing

### Production Mode:
- Cleaner interface
- Less verbose
- Better performance
- No debug overhead

## Troubleshooting Checklist

1. ✅ Server running on http://localhost:5001
2. ✅ API endpoints responding (test with curl)
3. ✅ Database connection established
4. ✅ No JavaScript errors in console
5. ✅ Network requests completing successfully
6. ✅ CORS headers properly set
7. ✅ Environment variables loaded
8. ✅ Browser cache cleared if needed

## Getting Help

### Gather Debug Information:
1. Screenshot of debug panel showing errors
2. Browser console logs
3. Network tab showing failed requests
4. Server-side logs from Python application

### Key Files:
- `/cosmos_db_viewer_debug.html` - Debug version
- `/cosmos_db_viewer.html` - Production version
- `/cosmos_viewer_server.py` - Backend API server

This guide should help you quickly identify and resolve frontend issues with the Cosmos DB viewer.