#!/bin/bash
# Setup script for Bloomberg Integration Project

echo "Bloomberg Integration Project Setup"
echo "==================================="

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Create project structure
echo "Creating project directories..."
mkdir -p deployment
mkdir -p integration
mkdir -p documentation
mkdir -p data/raw
mkdir -p data/processed
mkdir -p logs

# Create README in each directory
echo "Setting up directory structure..."

cat > deployment/README.md << 'EOF'
# Deployment Scripts

This directory contains deployment scripts for:
- Azure infrastructure provisioning
- VM configuration
- Network setup
- Security configuration
EOF

cat > integration/README.md << 'EOF'
# Integration Modules

This directory contains integration modules for:
- Bloomberg API connections
- Azure service integrations
- Data transformation pipelines
- Event streaming
EOF

cat > documentation/README.md << 'EOF'
# Documentation

Additional documentation for:
- API references
- Architecture diagrams
- Troubleshooting guides
- Best practices
EOF

cat > data/README.md << 'EOF'
# Data Directory

- `/raw` - Raw data from Bloomberg
- `/processed` - Processed and transformed data

Note: This directory is gitignored to prevent accidental data commits
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Data files
data/raw/*
data/processed/*
*.csv
*.parquet
*.pkl

# Logs
logs/*
*.log

# Environment
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
*.bak

# Credentials
*.pem
*.key
*.cer
*.pfx

# Keep directory structure
!data/raw/.gitkeep
!data/processed/.gitkeep
!logs/.gitkeep
EOF

# Create .gitkeep files
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch logs/.gitkeep

# Create environment template
cat > .env.template << 'EOF'
# Bloomberg Terminal VM Configuration
BLOOMBERG_VM_HOST=20.172.249.92
BLOOMBERG_VM_PRIVATE_IP=10.225.1.5
BLOOMBERG_VM_USERNAME=bloombergadmin
BLOOMBERG_VM_PASSWORD=your_password_here

# Bloomberg API Configuration
BLOOMBERG_API_HOST=localhost
BLOOMBERG_API_PORT=8194

# Azure Configuration
COSMOS_ENDPOINT=https://cosmos-research-analytics-prod.documents.azure.com:443/
COSMOS_KEY=your_cosmos_key_here
COSMOS_DATABASE=bloomberg-data
COSMOS_CONTAINER=market-data

EVENTHUB_NAMESPACE=central-data-hub-eus.servicebus.windows.net
EVENTHUB_NAME=bloomberg-stream
EVENTHUB_CONNECTION_STRING=your_eventhub_connection_string_here

# Key Vault
KEYVAULT_URL=https://bloomberg-kv-1752226585.vault.azure.net/

# News Collection
NEWS_COLLECTION_INTERVAL=30  # minutes
NEWS_SOURCES=bloomberg,reuters,ft,wsj
EOF

# Create run script
cat > run_news_collector.sh << 'EOF'
#!/bin/bash
# Run news collector script

echo "Starting News Collector..."
echo "========================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed!"
    exit 1
fi

# Navigate to script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Run the appropriate script based on Bloomberg availability
if [ -f ".env" ]; then
    source .env
fi

# Check if Bloomberg Terminal is accessible
if [ ! -z "$BLOOMBERG_VM_HOST" ]; then
    echo "Bloomberg configuration found"
    echo "To use Bloomberg integration, ensure:"
    echo "1. You're connected to the Bloomberg VM"
    echo "2. Bloomberg Terminal is running"
    echo "3. BLPAPI is accessible on port 8194"
    echo ""
fi

# Run general news collector (doesn't require Bloomberg)
echo "Running general news collector..."
python3 general_news_collector.py

# If Bloomberg is available, also run Bloomberg collector
# python3 bloomberg_news_collector.py
EOF

chmod +x run_news_collector.sh

# Create test script
cat > test_setup.sh << 'EOF'
#!/bin/bash
# Test the setup

echo "Testing Bloomberg Project Setup"
echo "=============================="

# Check Python
echo -n "Python 3: "
if command -v python3 &> /dev/null; then
    python3 --version
else
    echo "NOT FOUND"
fi

# Check directories
echo ""
echo "Project structure:"
for dir in deployment integration documentation data/raw data/processed logs; do
    if [ -d "$dir" ]; then
        echo "✓ $dir"
    else
        echo "✗ $dir MISSING"
    fi
done

# Check key files
echo ""
echo "Key files:"
for file in PROJECT_README.md bloomberg_azure_integration.py general_news_collector.py requirements.txt .gitignore; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file MISSING"
    fi
done

# Check environment
echo ""
echo "Environment:"
if [ -f ".env" ]; then
    echo "✓ .env file exists"
else
    echo "✗ .env file missing (copy from .env.template)"
fi

echo ""
echo "Setup test complete!"
EOF

chmod +x test_setup.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and add your credentials"
echo "2. Install Python dependencies: pip3 install -r requirements.txt"
echo "3. Test the setup: ./test_setup.sh"
echo "4. Run news collector: ./run_news_collector.sh"
echo ""
echo "For Bloomberg integration on VM:"
echo "- Connect to VM: RDP to 20.172.249.92"
echo "- Ensure Bloomberg Terminal is running"
echo "- Run: python bloomberg_news_collector.py"