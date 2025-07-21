# Deploy VM Control Endpoints to Bloomberg FastAPI Server

## Overview
This guide shows how to add VM service control and Azure VM management endpoints to the existing Bloomberg FastAPI server running on the VM.

## Files to Deploy

### 1. VM Service Control (`vm_service_control_endpoints.py`)
- **Purpose**: Control the Bloomberg FastAPI service itself (start/stop/restart)
- **Endpoints**:
  - `GET /api/vm/service/status` - Check if Bloomberg API service is running
  - `POST /api/vm/service/start` - Start the Bloomberg API service
  - `POST /api/vm/service/stop` - Stop the Bloomberg API service  
  - `POST /api/vm/service/restart` - Restart the Bloomberg API service

### 2. Azure VM Control (`azure_vm_control_endpoints.py`)
- **Purpose**: Control the entire Azure VM (start/stop/restart)
- **Endpoints**:
  - `GET /api/azure/vm/status` - Get Azure VM status
  - `POST /api/azure/vm/start` - Start the Azure VM
  - `POST /api/azure/vm/stop` - Stop (deallocate) the Azure VM
  - `POST /api/azure/vm/restart` - Restart the Azure VM

## Deployment Steps

### Step 1: Upload Files to Bloomberg VM
```powershell
# Copy files to Bloomberg VM
Copy-Item -Path "vm_service_control_endpoints.py" -Destination "C:\BloombergAPI\"
Copy-Item -Path "azure_vm_control_endpoints.py" -Destination "C:\BloombergAPI\"
```

### Step 2: Update main.py to Include New Endpoints
Add these imports and function calls to your existing `main.py`:

```python
# Add these imports at the top
from vm_service_control_endpoints import add_service_control_endpoints
from azure_vm_control_endpoints import add_azure_vm_control_endpoints

# Add these lines after creating the FastAPI app but before starting the server
add_service_control_endpoints(app)
add_azure_vm_control_endpoints(app)
```

### Step 3: Install Additional Dependencies
```powershell
cd C:\BloombergAPI
pip install psutil asyncio
```

### Step 4: Install Azure CLI (for VM control)
```powershell
# Download and install Azure CLI
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'

# Login to Azure (run this once)
az login
```

### Step 5: Restart Bloomberg API Service
```powershell
# Stop current service
Stop-Process -Name "python" -Force

# Start with new endpoints
cd C:\BloombergAPI
python main.py
```

## Testing the New Endpoints

### Test VM Service Control
```bash
# Check service status
curl http://20.172.249.92:8080/api/vm/service/status

# Start service (if stopped)
curl -X POST http://20.172.249.92:8080/api/vm/service/start \
  -H "Authorization: Bearer test"

# Stop service
curl -X POST http://20.172.249.92:8080/api/vm/service/stop \
  -H "Authorization: Bearer test"
```

### Test Azure VM Control
```bash
# Check VM status
curl http://20.172.249.92:8080/api/azure/vm/status \
  -H "Authorization: Bearer test"

# Start VM (if stopped)
curl -X POST http://20.172.249.92:8080/api/azure/vm/start \
  -H "Authorization: Bearer test"
```

## Frontend Integration

The frontend is already updated to use these endpoints:
- `bloomberg.ts` has `startBloombergService()`, `stopBloombergService()`, `getServiceStatus()`
- `Header.tsx` will show real VM service status and provide start/stop controls

## Expected Responses

### Service Status Response
```json
{
  "success": true,
  "service_running": true,
  "process_count": 1,
  "processes": [
    {
      "pid": 1234,
      "status": "running",
      "cmdline": "python.exe C:\\BloombergAPI\\main.py"
    }
  ],
  "timestamp": "2025-07-17T10:05:00.000000",
  "vm_status": "running"
}
```

### VM Status Response
```json
{
  "success": true,
  "vm_status": "VM running",
  "vm_size": "Standard_D4s_v3",
  "location": "eastus",
  "public_ip": "20.172.249.92",
  "private_ip": "10.225.1.4",
  "provisioning_state": "Succeeded",
  "resource_group": "bloomberg-terminal-rg",
  "vm_name": "bloomberg-vm-02"
}
```

## Security Considerations

1. **Authentication**: All endpoints require Bearer token authentication
2. **Authorization**: Ensure only authorized users can start/stop VMs
3. **Audit Logging**: All VM control actions are logged
4. **Azure Permissions**: Ensure the VM has proper Azure CLI permissions

## Troubleshooting

### Service Control Issues
- Check if `psutil` is installed: `pip install psutil`
- Verify Bloomberg API files exist at `C:\BloombergAPI\`
- Check Windows Event Logs for service errors

### Azure VM Control Issues  
- Verify Azure CLI is installed: `az --version`
- Check Azure login: `az account show`
- Ensure proper Azure permissions for VM operations
- Check Azure subscription and resource group names

### Network Issues
- Verify firewall rules allow API access on port 8080
- Check Azure Network Security Group rules
- Test connectivity: `Test-NetConnection -ComputerName localhost -Port 8080`

## Important Notes

1. **VM Control Power**: Azure VM control can start/stop the entire machine - use carefully
2. **Service Control Safety**: Service control only affects the Bloomberg API process
3. **Authentication Required**: All control endpoints require proper authentication
4. **Logging**: All operations are logged for audit purposes
5. **Timeouts**: VM operations have 5-minute timeouts to handle Azure delays

This implementation provides complete control over both the Bloomberg FastAPI service and the Azure VM itself, giving you full infrastructure management capability from the React frontend.