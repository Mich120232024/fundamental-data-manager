#!/bin/bash
# AI News Monitor execution script

# Set up environment
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
# Load environment variables from .env file
source "/Users/mikaeleage/Research & Analytics Services/.env"

# Change to script directory
cd "/Users/mikaeleage/Research & Analytics Services"

# Log file with date
LOG_FILE="/Users/mikaeleage/Research & Analytics Services/ai_news_monitor/logs/ai_news_$(date +%Y%m%d).log"

echo "======================================" >> "$LOG_FILE"
echo "AI News Monitor Started: $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

# Run the Python script with Poetry
/opt/homebrew/bin/poetry run python ai_news_monitor/ai_news_agent_local.py >> "$LOG_FILE" 2>&1

echo "Completed: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
