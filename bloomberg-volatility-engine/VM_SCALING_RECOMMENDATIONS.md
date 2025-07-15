# Bloomberg VM Performance Scaling Recommendations

## Current Configuration
- **VM**: bloomberg-vm-02
- **Size**: Standard_D4s_v5
- **vCPUs**: 4
- **Memory**: 16 GB
- **Location**: East US

## Performance Issues
Running simultaneously:
- Bloomberg Terminal (heavy resource usage)
- Cursor IDE
- Gemini CLI
- Python API server
- Browser for testing

## Recommended Scaling Options

### Option 1: Standard_D8s_v5 (Moderate Upgrade) ⭐ RECOMMENDED
- **vCPUs**: 8 (2x current)
- **Memory**: 32 GB (2x current)
- **Cost**: ~$280/month
- **Benefits**:
  - Double the CPU cores for parallel processing
  - Double RAM for better application performance
  - Good balance of cost and performance
  - Same SSD performance tier

### Option 2: Standard_D16s_v5 (High Performance)
- **vCPUs**: 16 (4x current)
- **Memory**: 64 GB (4x current)
- **Cost**: ~$560/month
- **Benefits**:
  - Excellent for heavy development
  - Run multiple browsers and tools
  - Future-proof for additional services
  - Smooth experience with all tools

### Option 3: Standard_E8s_v5 (Memory Optimized)
- **vCPUs**: 8
- **Memory**: 64 GB (4x current)
- **Cost**: ~$360/month
- **Benefits**:
  - Same CPU upgrade as D8s_v5
  - Much more memory for data processing
  - Better for Bloomberg data caching
  - Good for memory-intensive operations

## Immediate Optimization Steps (Before Scaling)

### 1. Stop Unnecessary Services
```powershell
# Check running processes
Get-Process | Sort-Object -Property WS -Descending | Select-Object -First 20

# Stop Windows Search if not needed
Stop-Service -Name "WSearch" -Force
Set-Service -Name "WSearch" -StartupType Disabled

# Disable Windows Defender real-time (temporarily for dev)
Set-MpPreference -DisableRealtimeMonitoring $true
```

### 2. Optimize Bloomberg Terminal
```powershell
# Reduce Bloomberg Terminal windows
# Close unused Bloomberg panels
# Disable Bloomberg news feed if not needed
```

### 3. Optimize Cursor IDE
- Disable unnecessary extensions
- Increase memory allocation in settings
- Disable file watchers for node_modules

### 4. Configure Page File
```powershell
# Increase virtual memory
wmic computersystem set AutomaticManagedPagefile=False
wmic pagefileset where name="C:\\pagefile.sys" set InitialSize=24576,MaximumSize=32768
```

## Scaling Commands

### To Resize VM (Requires Restart)
```bash
# Deallocate VM first
az vm deallocate -g bloomberg-terminal-rg -n bloomberg-vm-02

# Resize to D8s_v5
az vm resize -g bloomberg-terminal-rg -n bloomberg-vm-02 --size Standard_D8s_v5

# Start VM
az vm start -g bloomberg-terminal-rg -n bloomberg-vm-02
```

### To Create Dev-Time Snapshot (Before Scaling)
```bash
# Create snapshot for rollback
az snapshot create \
  -g bloomberg-terminal-rg \
  -n bloomberg-vm-02-snapshot-$(date +%Y%m%d) \
  --source /subscriptions/6f928fec-8d15-47d7-b27b-be8b568e9789/resourceGroups/bloomberg-terminal-rg/providers/Microsoft.Compute/disks/bloomberg-vm-02_OsDisk_1_*
```

## Alternative: Separate Development VM

Consider creating a dedicated development VM:

```bash
# Create a new dev VM with better specs
az vm create \
  -g bloomberg-terminal-rg \
  -n bloomberg-dev-vm \
  --image Win2022AzureEditionCore \
  --size Standard_D8s_v5 \
  --admin-username devadmin \
  --admin-password 'YourSecurePassword123!' \
  --public-ip-sku Standard
```

## Performance Monitoring

### Check Current Resource Usage
```powershell
# CPU and Memory usage
Get-Counter '\Processor(_Total)\% Processor Time','\Memory\Available MBytes' -Continuous -SampleInterval 2

# Disk I/O
Get-Counter '\PhysicalDisk(_Total)\Disk Reads/sec','\PhysicalDisk(_Total)\Disk Writes/sec'

# Process specific usage
Get-Process cursor, bloomberg*, python | Select-Object Name, CPU, WS, VM
```

## Cost Optimization Tips

1. **Auto-shutdown**: Configure VM to shutdown at night
```bash
az vm auto-shutdown \
  -g bloomberg-terminal-rg \
  -n bloomberg-vm-02 \
  --time 2300 \
  --timezone "Eastern Standard Time"
```

2. **Weekend Scaling**: Use automation to downsize on weekends
3. **Spot Instances**: For dev/test workloads (not recommended for Bloomberg Terminal)

## Recommendation Summary

For immediate relief, I recommend:
1. **Upgrade to Standard_D8s_v5** - Best balance of performance and cost
2. **Implement the optimization steps** before scaling
3. **Monitor performance** after upgrade
4. **Consider E8s_v5** if memory is the main bottleneck

The upgrade process takes about 10-15 minutes with VM restart required.

—SOFTWARE_RESEARCH_ANALYST