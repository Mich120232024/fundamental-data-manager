# Claude Code MCP Server - Asyncio Fix Summary

## Issue
The Claude Code MCP server was failing in Kubernetes with the error:
```
RuntimeError: asyncio.run() cannot be called from a running event loop
```

This occurred because the container environment already had an asyncio event loop running when the script tried to create a new one with `asyncio.run(main())`.

## Root Cause
The original code at line 292 in `mcp_server_corrected.py` was using:
```python
asyncio.run(main())
```

This fails in containerized environments where an event loop may already be running.

## Solution
Modified the startup sequence to:
1. Setup Azure integration synchronously
2. Run the health check server in a separate thread (avoiding asyncio conflicts)
3. Create and manage the event loop explicitly
4. Run the MCP server on the main thread with stdio transport

## Key Changes in `mcp_server_corrected.py`

1. Removed the `main()` async function that was trying to run both servers
2. Changed the startup pattern to:
   - Create a new event loop explicitly
   - Run health server in a background thread
   - Run MCP server on the main thread

```python
# Create a new event loop for the entire application
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Run health server in background thread
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()

# Run MCP server on main thread
loop.run_until_complete(mcp.run())
```

## Deployment Instructions

1. **Rebuild the Docker image:**
   ```bash
   docker build -f Dockerfile.corrected -t gzcacr.azurecr.io/claude-code-server:v1.0.35 .
   ```

2. **Push to Azure Container Registry:**
   ```bash
   docker push gzcacr.azurecr.io/claude-code-server:v1.0.35
   ```

3. **Update the Kubernetes deployment:**
   ```bash
   # Update the image version in claude-code-deployment.yaml
   # Change line 49 from:
   # image: gzcacr.azurecr.io/claude-code-server:v1.0.34
   # to:
   # image: gzcacr.azurecr.io/claude-code-server:v1.0.35
   
   kubectl apply -f claude-code-deployment.yaml
   ```

4. **Monitor the deployment:**
   ```bash
   kubectl -n gzc-trading get pods -w
   kubectl -n gzc-trading logs -f deployment/claude-code-server
   ```

## Testing
After deployment, verify:
1. Health check endpoint: `curl http://claude-code-service/health`
2. Readiness endpoint: `curl http://claude-code-service/ready`
3. Check logs for successful startup messages
4. Verify MCP server is accepting connections on stdio

## Benefits
- Eliminates asyncio conflicts in containerized environments
- Separates health check server from MCP server operation
- More robust startup sequence for Kubernetes
- Better error handling and logging