# Bloomberg API VM Networking Configuration

## Related Documentation
- **[README](./README.md)**: Complete system overview and infrastructure details
- **[API Endpoints](./API_ENDPOINTS.md)**: API endpoint documentation and performance metrics
- **[Data Retrieval Methodology](./DATA_RETRIEVAL_METHODOLOGY.md)**: Implementation patterns and caching strategies
- **[Volatility Formats](./VOLATILITY_FORMATS.md)**: Bloomberg security formats and performance considerations
- **[Setup Guide](./SETUP_GUIDE.md)**: VM setup and network configuration procedures

## Network Architecture Overview

### Current Network Topology
```
Client (localhost:5173) 
    ↓ [Vite Proxy]
Bloomberg VM (20.172.249.92:8080)
    ↓ [Bloomberg API]
Bloomberg Terminal (localhost:8194)
    ↓ [Bloomberg Network]
Bloomberg Data Centers
```

### Azure Network Integration
- **VNet**: Integrated with main AKS VNet
- **Subnet**: `10.225.1.0/24`
- **Private IP**: `10.225.1.5`
- **Public IP**: `20.172.249.92`
- **Resource Group**: `bloomberg-terminal-rg`

## VNet Configuration

### 1. VNet Consolidation
Originally, Bloomberg VM was in a separate VNet. We consolidated it into the main AKS VNet for better integration.

#### Before (Separate VNet)
```
├── bloomberg-vnet (10.224.0.0/16)
│   └── bloomberg-subnet (10.224.1.0/24)
│       └── bloomberg-vm-02 (10.224.1.4)
└── main-aks-vnet (10.225.0.0/16)
    ├── aks-subnet (10.225.0.0/24)
    ├── db-subnet (10.225.2.0/24)
    └── services-subnet (10.225.3.0/24)
```

#### After (Consolidated VNet)
```
main-aks-vnet (10.225.0.0/16)
├── aks-subnet (10.225.0.0/24)
├── bloomberg-subnet (10.225.1.0/24)
│   └── bloomberg-vm-02 (10.225.1.5)
├── db-subnet (10.225.2.0/24)
└── services-subnet (10.225.3.0/24)
```

### 2. VNet Integration Commands
```bash
# Move VM to main VNet
az vm deallocate --resource-group bloomberg-terminal-rg --name bloomberg-vm-02

# Update NIC configuration
az network nic ip-config update \
  --resource-group bloomberg-terminal-rg \
  --nic-name bloomberg-vm-02VMNic \
  --name ipconfigbloomberg-vm-02 \
  --vnet-name main-aks-vnet \
  --subnet bloomberg-subnet \
  --private-ip-address 10.225.1.5

# Start VM
az vm start --resource-group bloomberg-terminal-rg --name bloomberg-vm-02
```

## Network Security Groups (NSG)

### 1. Inbound Rules
```bash
# Rule 1: Allow RDP (3389)
az network nsg rule create \
  --resource-group bloomberg-terminal-rg \
  --nsg-name bloomberg-vm-02NSG \
  --name AllowRDP \
  --protocol tcp \
  --priority 1000 \
  --destination-port-range 3389 \
  --source-address-prefix "VirtualNetwork" \
  --access allow

# Rule 2: Allow API Access (8080)
az network nsg rule create \
  --resource-group bloomberg-terminal-rg \
  --nsg-name bloomberg-vm-02NSG \
  --name AllowAPI \
  --protocol tcp \
  --priority 1001 \
  --destination-port-range 8080 \
  --source-address-prefix "*" \
  --access allow

# Rule 3: Allow Bloomberg Terminal (8194)
az network nsg rule create \
  --resource-group bloomberg-terminal-rg \
  --nsg-name bloomberg-vm-02NSG \
  --name AllowBloombergTerminal \
  --protocol tcp \
  --priority 1002 \
  --destination-port-range 8194 \
  --source-address-prefix "VirtualNetwork" \
  --access allow

# Rule 4: Allow HTTPS (443) for Bloomberg updates
az network nsg rule create \
  --resource-group bloomberg-terminal-rg \
  --nsg-name bloomberg-vm-02NSG \
  --name AllowHTTPS \
  --protocol tcp \
  --priority 1003 \
  --destination-port-range 443 \
  --source-address-prefix "*" \
  --access allow
```

### 2. Outbound Rules
```bash
# Allow all outbound (default)
# Bloomberg Terminal requires various outbound connections
# API server needs outbound for logging and monitoring
```

## Port Configuration

### 1. Bloomberg API Server
- **Port**: `8080`
- **Protocol**: `HTTP`
- **Binding**: `0.0.0.0:8080` (all interfaces)
- **Access**: Public and private networks

### 2. Bloomberg Terminal
- **Port**: `8194`
- **Protocol**: `TCP`
- **Binding**: `localhost:8194`
- **Access**: Local VM only

### 3. System Ports
- **RDP**: `3389`
- **HTTP**: `80`
- **HTTPS**: `443`
- **WinRM**: `5985`, `5986`

## Client-Side Configuration

### 1. Vite Proxy Setup
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://20.172.249.92:8080',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Proxying request:', req.method, req.url);
          });
        }
      }
    }
  }
});
```

### 2. Environment Configuration
```bash
# Development environment
VITE_BLOOMBERG_API_BASE_URL=http://localhost:5173/api
VITE_BLOOMBERG_API_TOKEN=test

# Production environment
VITE_BLOOMBERG_API_BASE_URL=http://20.172.249.92:8080/api
VITE_BLOOMBERG_API_TOKEN=test
```

## Network Connectivity Testing

### 1. Basic Connectivity
```bash
# Test VM reachability
ping 20.172.249.92

# Test API port
telnet 20.172.249.92 8080
# Or using netcat
nc -zv 20.172.249.92 8080
```

### 2. API Health Check
```bash
# Direct API call
curl -v http://20.172.249.92:8080/health

# Through proxy (development)
curl -v http://localhost:5173/api/health
```

### 3. Network Trace
```bash
# Traceroute to VM
traceroute 20.172.249.92

# MTR for continuous monitoring
mtr 20.172.249.92
```

## DNS Configuration

### 1. Azure DNS
```bash
# Check DNS resolution
nslookup 20.172.249.92
nslookup bloomberg-vm-02.eastus.cloudapp.azure.com
```

### 2. Custom DNS (Optional)
```bash
# Create DNS zone
az network dns zone create \
  --resource-group bloomberg-terminal-rg \
  --name bloomberg.local

# Add A record
az network dns record-set a add-record \
  --resource-group bloomberg-terminal-rg \
  --zone-name bloomberg.local \
  --record-set-name api \
  --ipv4-address 20.172.249.92
```

## Load Balancing and High Availability

### 1. Single VM Configuration (Current)
- Single point of failure
- Bloomberg Terminal license limits
- Manual failover required

### 2. Future Multi-VM Setup
```bash
# Create load balancer
az network lb create \
  --resource-group bloomberg-terminal-rg \
  --name bloomberg-lb \
  --sku Standard \
  --public-ip-address bloomberg-lb-ip

# Create backend pool
az network lb address-pool create \
  --resource-group bloomberg-terminal-rg \
  --lb-name bloomberg-lb \
  --name bloomberg-backend-pool

# Create health probe
az network lb probe create \
  --resource-group bloomberg-terminal-rg \
  --lb-name bloomberg-lb \
  --name health-probe \
  --protocol http \
  --port 8080 \
  --path /health
```

## Monitoring and Logging

### 1. Network Monitoring
```bash
# Network performance counters
# Monitor bandwidth usage
# Track connection counts
# Alert on network failures
```

### 2. Connection Logging
```python
# API server logs network connections
logger.info(f"API request from {request.client.host}:{request.client.port}")
logger.info(f"Bloomberg Terminal connection to localhost:8194")
```

## Firewall Configuration

### 1. Windows Firewall (VM)
```powershell
# Allow API server
New-NetFirewallRule -DisplayName "Bloomberg API Server" -Direction Inbound -Port 8080 -Protocol TCP -Action Allow

# Allow Bloomberg Terminal
New-NetFirewallRule -DisplayName "Bloomberg Terminal API" -Direction Inbound -Port 8194 -Protocol TCP -Action Allow

# Allow outbound Bloomberg connections
New-NetFirewallRule -DisplayName "Bloomberg Outbound" -Direction Outbound -Protocol TCP -Action Allow
```

### 2. Azure Firewall (Optional)
```bash
# Create firewall rules for Bloomberg traffic
# Allow specific Bloomberg IP ranges
# Block unauthorized access attempts
```

## VPN and Private Connectivity

### 1. Site-to-Site VPN
```bash
# Create VPN gateway
az network vnet-gateway create \
  --resource-group bloomberg-terminal-rg \
  --name bloomberg-vpn-gateway \
  --vnet main-aks-vnet \
  --gateway-type Vpn \
  --vpn-type RouteBased \
  --sku VpnGw1

# Configure on-premises connection
az network local-gateway create \
  --resource-group bloomberg-terminal-rg \
  --name on-premises-gateway \
  --gateway-ip-address <ON_PREMISES_IP> \
  --local-address-prefixes <ON_PREMISES_CIDR>
```

### 2. Private Endpoints
```bash
# Create private endpoint for secure access
az network private-endpoint create \
  --resource-group bloomberg-terminal-rg \
  --name bloomberg-private-endpoint \
  --vnet-name main-aks-vnet \
  --subnet bloomberg-subnet \
  --private-connection-resource-id <RESOURCE_ID> \
  --group-ids <GROUP_ID>
```

## Network Performance Optimization

### 1. Bandwidth Optimization
- **Configure appropriate VM size** for network requirements
- **Use premium storage** for better IOPS
- **Implement connection pooling** for Bloomberg connections
- **Data compression** for historical data transfers
- **Batch processing** to reduce total network requests

### 2. Latency Reduction
- **Place VM in same region** as clients
- **Use Azure CDN** for static content
- **Implement proper caching strategies**:
  - Live data: No caching
  - EOD data: Cache until next market close
  - Historical data: Cache with daily refresh
- **Connection keep-alive** for Bloomberg Terminal

### 3. Connection Management
```python
# API server connection pooling
class BloombergConnectionPool:
    def __init__(self, max_connections=5):
        self.pool = []
        self.max_connections = max_connections
    
    def get_connection(self):
        # Reuse existing connection or create new
        pass
    
    def health_check(self):
        # Monitor connection health
        pass

# Implement connection health checks
def check_bloomberg_connection():
    try:
        # Test connection with simple request
        response = bloomberg.get_reference_data(["EURUSD Curncy"], ["PX_LAST"])
        return response is not None
    except Exception:
        return False
```

### 4. Data Type Specific Optimizations
- **Live Data**: Use WebSocket connections for real-time updates
- **EOD Data**: Batch requests for multiple currency pairs
- **Historical Data**: Use streaming for large datasets
- **Caching**: Implement Redis for distributed caching

## Security Considerations

### 1. Network Security
- Use NSG rules to restrict access
- Implement proper authentication
- Monitor network traffic

### 2. Data Encryption
- Use HTTPS for production
- Encrypt data in transit
- Secure API keys

### 3. Access Control
- Implement role-based access
- Use Azure AD integration
- Monitor access patterns

## Troubleshooting Network Issues

### 1. Connection Refused
```bash
# Check if API server is running
curl -v http://20.172.249.92:8080/health

# Check port accessibility
telnet 20.172.249.92 8080

# Test specific endpoints
curl -X POST http://20.172.249.92:8080/api/fx/volatility/live \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"currency_pairs": ["EURUSD"], "tenors": ["1M"]}'
```

### 2. DNS Resolution
```bash
# Test DNS resolution
nslookup 20.172.249.92
dig 20.172.249.92

# Check reverse DNS
dig -x 20.172.249.92
```

### 3. Network Routing
```bash
# Check routing table
route -n
ip route show

# Trace route to Bloomberg VM
traceroute 20.172.249.92
mtr 20.172.249.92
```

### 4. Firewall Issues
```powershell
# Check Windows Firewall
Get-NetFirewallRule -DisplayName "*Bloomberg*"

# Test connectivity
Test-NetConnection -ComputerName 20.172.249.92 -Port 8080

# Check specific ports
Test-NetConnection -ComputerName 20.172.249.92 -Port 8194
```

### 5. Performance Issues
```bash
# Monitor network latency
ping -c 100 20.172.249.92

# Check bandwidth usage
iftop -i eth0

# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s http://20.172.249.92:8080/health
```

### 6. Bloomberg Terminal Connectivity
```powershell
# Check Bloomberg Terminal process
Get-Process -Name "bloomberg*"

# Test Bloomberg API connection
Test-NetConnection -ComputerName localhost -Port 8194

# Check Bloomberg Terminal logs
Get-EventLog -LogName Application -Source "Bloomberg" -Newest 10
```

## Performance Metrics

### 1. Network Latency by Data Type
- **Live data**: 200-500ms per request
- **EOD data**: 300-800ms per request
- **Historical data**: 500-2000ms per request
- **Batch requests**: 1000-5000ms for multiple securities
- **Bloomberg Terminal response**: 100-300ms
- **Network round-trip**: 50-100ms

### 2. Bandwidth Usage by Data Type
- **Live API requests**: 1-10 KB per request
- **EOD API requests**: 5-20 KB per request
- **Historical API requests**: 20-200 KB per request
- **Bloomberg data responses**: 1-100 KB per response
- **Historical data responses**: 100-1000 KB per response
- **Total bandwidth**: 1-50 Mbps during heavy usage

### 3. Connection Counts
- **Concurrent API connections**: 10-100
- **Bloomberg Terminal connections**: 1-5
- **Historical data connections**: 1-3 (long-running)
- **Total connections**: 20-200

## Network Monitoring

### 1. Real-time Monitoring
```bash
# Monitor network connections
netstat -an | grep :8080

# Monitor active connections
ss -tuln | grep :8080

# Monitor bandwidth usage
iftop -i eth0
```

### 2. Performance Monitoring
```powershell
# Monitor network performance counters
Get-Counter "\Network Interface(*)\Bytes Total/sec"
Get-Counter "\Network Interface(*)\Packets/sec"

# Monitor API response times
Get-Content "C:\BloombergAPI\logs\performance.log" | Select-String "response_time"
```

### 3. Alerting
```python
# Network monitoring script
import psutil
import requests
import time

def monitor_network():
    while True:
        # Check network connectivity
        try:
            response = requests.get("http://20.172.249.92:8080/health", timeout=5)
            if response.status_code != 200:
                send_alert("API health check failed")
        except requests.RequestException:
            send_alert("Network connectivity lost")
        
        # Check bandwidth usage
        net_io = psutil.net_io_counters()
        if net_io.bytes_sent > THRESHOLD:
            send_alert("High bandwidth usage detected")
        
        time.sleep(60)
```

---

*Last Updated: July 16, 2025*
*Status: Production Ready - Complete Network Documentation*
*Coverage: Live, EOD, and Historical Data Network Considerations*