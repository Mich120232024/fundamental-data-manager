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
