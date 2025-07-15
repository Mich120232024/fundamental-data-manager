#!/bin/bash
# Configure network access for Bloomberg API Server

echo "Configuring Bloomberg API Server Network Access"
echo "=============================================="

# Variables
RESOURCE_GROUP="bloomberg-terminal-rg"
NSG_NAME="bloomberg-nsg"
API_PORT="8080"

# Get current public IP
echo -e "\n1. Getting your current public IP..."
CURRENT_IP=$(curl -s https://api.ipify.org)
echo "   Your IP: $CURRENT_IP"

# Add NSG rule for API access
echo -e "\n2. Adding NSG rule for Bloomberg API Server..."
az network nsg rule create \
    --resource-group $RESOURCE_GROUP \
    --nsg-name $NSG_NAME \
    --name "Allow-Bloomberg-API" \
    --priority 110 \
    --direction Inbound \
    --access Allow \
    --protocol Tcp \
    --source-address-prefixes "$CURRENT_IP/32" \
    --source-port-ranges "*" \
    --destination-address-prefixes "*" \
    --destination-port-ranges $API_PORT \
    --description "Allow Bloomberg API Server access"

if [ $? -eq 0 ]; then
    echo "   ✓ NSG rule created successfully"
else
    echo "   ✗ Failed to create NSG rule"
fi

# For internal VNet access
echo -e "\n3. Adding NSG rule for VNet internal access..."
az network nsg rule create \
    --resource-group $RESOURCE_GROUP \
    --nsg-name $NSG_NAME \
    --name "Allow-VNet-Bloomberg-API" \
    --priority 111 \
    --direction Inbound \
    --access Allow \
    --protocol Tcp \
    --source-address-prefixes "10.224.0.0/12" \
    --source-port-ranges "*" \
    --destination-address-prefixes "*" \
    --destination-port-ranges $API_PORT \
    --description "Allow Bloomberg API Server access from VNet"

if [ $? -eq 0 ]; then
    echo "   ✓ VNet access rule created successfully"
else
    echo "   ✗ Failed to create VNet access rule"
fi

# Show all NSG rules
echo -e "\n4. Current NSG rules:"
az network nsg rule list \
    --resource-group $RESOURCE_GROUP \
    --nsg-name $NSG_NAME \
    --output table \
    --query "[].{Name:name, Priority:priority, SourceAddress:sourceAddressPrefixes[0], DestPort:destinationPortRanges[0], Access:access}"

echo -e "\n✅ Network configuration complete!"
echo "   - External access: $CURRENT_IP -> Port $API_PORT"
echo "   - Internal access: 10.224.0.0/12 -> Port $API_PORT"
echo -e "\n📝 Next steps:"
echo "   1. RDP to VM: $CURRENT_IP -> 20.172.249.92"
echo "   2. Copy bloomberg_api_server.py to C:\\Bloomberg\\APIServer"
echo "   3. Run setup_bloomberg_service.ps1 as Administrator"
echo "   4. Test API at: http://20.172.249.92:8080/docs"