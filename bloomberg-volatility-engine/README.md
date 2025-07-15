# Bloomberg Terminal Azure Deployment

## Overview
Bloomberg Terminal deployment on Azure VM with full integration to Azure services through private endpoints.

## Architecture

```
AKS VNet (10.224.0.0/12) - East US
├── Bloomberg Subnet (10.225.1.0/24)
│   └── Bloomberg Terminal VM (10.225.1.4)
├── Private Endpoints Subnet (10.225.2.0/24)
│   ├── Cosmos DB PE (10.225.2.4)
│   └── Event Hub PE (10.225.2.6)
└── AKS Subnet (10.224.0.0/16)
    └── Kubernetes Services
```

## Deployed Resources

### 1. Bloomberg Terminal VM
- **Name**: bloomberg-vm-01
- **Resource Group**: bloomberg-terminal-rg
- **Private IP**: 10.225.1.4
- **Public IP**: 172.171.211.16
- **Size**: Standard_D4s_v5
- **OS**: Windows Server 2022 Azure Edition
- **Managed Identity**: bloomberg-vm-identity

### 2. Network Configuration
- **VNet**: aks-vnet-18978512 (existing AKS VNet)
- **Bloomberg Subnet**: 10.225.1.0/24
- **Private Endpoints Subnet**: 10.225.2.0/24
- **NSG**: bloomberg-nsg (RDP access restricted)

### 3. Private Endpoints
- **Cosmos DB**: cosmos-analytics-pe
  - Target: cosmos-research-analytics-prod
  - Private IP: 10.225.2.4
- **Event Hub**: eventhub-pe  
  - Target: central-data-hub-eus
  - Private IP: 10.225.2.6

### 4. Security Resources
- **Key Vault**: bloomberg-kv-1752226585
- **Managed Identity**: bloomberg-vm-identity
- **RBAC**: Key Vault Secrets User role assigned

## Installation Steps

### 1. Connect to VM
```bash
# RDP Connection
Server: 172.171.211.16
Username: bloombergadmin
Password: Bl00mb3rg@Azure2025!
```

### 2. Run Installation Script
1. Copy `install_bloomberg_terminal.ps1` to the VM
2. Run as Administrator:
```powershell
.\install_bloomberg_terminal.ps1
```

### 3. Install Bloomberg Terminal
1. Contact Bloomberg Support:
   - US: +1 212 318 2000
   - Europe: +44 20 7330 7500
   - Email: support@bloomberg.net
2. Request Windows installer for Azure VM
3. Run installer and authenticate

### 4. Setup Python Integration
After Bloomberg installation:
```bash
python C:\blp\setup_bloomberg_api.py
```

### 5. Deploy Integration Service
1. Copy `bloomberg_azure_integration.py` to VM
2. Configure environment variables or Key Vault secrets:
   - cosmos-primary-key
   - eventhub-connection-string
3. Run the service:
```bash
python bloomberg_azure_integration.py
```

## Azure CLI Commands Reference

### Create Resources
```bash
# Resource Group
az group create --name bloomberg-terminal-rg --location eastus

# Subnets
az network vnet subnet create \
  --resource-group MC_gzc-kubernetes-rg_gzc-k8s-engine_eastus \
  --vnet-name aks-vnet-18978512 \
  --name bloomberg-subnet \
  --address-prefixes 10.225.1.0/24

# VM
az vm create \
  --resource-group bloomberg-terminal-rg \
  --name bloomberg-vm-01 \
  --image Win2022AzureEditionCore \
  --size Standard_D4s_v5 \
  --subnet $SUBNET_ID \
  --admin-username bloombergadmin
```

### Private Endpoints
```bash
# Cosmos DB
az network private-endpoint create \
  --name cosmos-analytics-pe \
  --resource-group bloomberg-terminal-rg \
  --subnet $SUBNET_ID \
  --private-connection-resource-id $COSMOS_ID \
  --group-id Sql

# Event Hub  
az network private-endpoint create \
  --name eventhub-pe \
  --resource-group bloomberg-terminal-rg \
  --subnet $SUBNET_ID \
  --private-connection-resource-id $EVENTHUB_ID \
  --group-id namespace
```

## Python BLPAPI Integration

The `bloomberg_azure_integration.py` script provides:
- Bloomberg Terminal API connection (localhost:8194)
- Cosmos DB integration via private endpoint
- Event Hub streaming via private endpoint
- Managed Identity authentication
- Continuous data updates

### Example Usage
```python
securities = ["EURUSD Curncy", "GBPUSD Curncy"]
fields = ["PX_LAST", "PX_BID", "PX_ASK"]

service = BloombergAzureIntegration()
service.run_continuous_update(securities, fields, interval=60)
```

## Troubleshooting

### Bloomberg Connection Issues
1. Verify Bloomberg Terminal is running
2. Check Windows Firewall rules
3. Confirm port 8194 is accessible locally
4. Ensure user is logged into Bloomberg

### Azure Connection Issues
1. Verify private endpoints are provisioned
2. Check managed identity permissions
3. Confirm Key Vault access policies
4. Test DNS resolution for private endpoints

### DNS Configuration (Optional)
For private endpoint DNS resolution:
```bash
# Add private DNS zones
az network private-dns zone create \
  --resource-group bloomberg-terminal-rg \
  --name privatelink.documents.azure.com

# Link to VNet
az network private-dns link vnet create \
  --resource-group bloomberg-terminal-rg \
  --zone-name privatelink.documents.azure.com \
  --name bloomberg-link \
  --virtual-network aks-vnet-18978512
```

## Maintenance

### VM Management
- Regular Windows Updates
- Bloomberg Terminal updates
- Python package updates
- Security patches

### Monitoring
- Azure Monitor for VM metrics
- Application Insights for Python app
- Event Hub metrics
- Cosmos DB metrics

## Cost Optimization

### Estimated Monthly Costs
- VM (D4s_v5): ~$140
- Storage: ~$20
- Private Endpoints: ~$10/each
- Data Transfer: Variable
- **Total**: ~$180 + data transfer

### Cost Saving Options
1. Use Azure Hybrid Benefit for Windows
2. Reserved Instance for VM (1-3 year)
3. Auto-shutdown during non-trading hours
4. Right-size VM based on usage

## Security Best Practices

1. **Network Security**
   - Keep NSG rules restrictive
   - Use Azure Bastion for RDP
   - Enable Azure Firewall

2. **Identity & Access**
   - Use managed identity only
   - Rotate passwords regularly
   - Enable MFA for Bloomberg

3. **Data Protection**
   - Enable encryption at rest
   - Use private endpoints only
   - Regular backups

4. **Compliance**
   - Follow Bloomberg's terms of service
   - Audit access logs
   - Monitor data usage

---

**Created by**: HEAD_OF_ENGINEERING  
**Date**: 2025-07-11  
**Status**: Deployed and Operational