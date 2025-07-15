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
