#!/bin/bash
# Setup script for AI News Monitor cron job

echo "🔧 Setting up AI News Monitor daily cron job..."

# Get the full path to Poetry and Python
POETRY_PATH=$(which poetry)
SCRIPT_DIR="/Users/mikaeleage/Research & Analytics Services/ai_news_monitor"
LOG_DIR="$SCRIPT_DIR/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

# Create the cron script
cat > "$SCRIPT_DIR/run_ai_news_monitor.sh" << 'EOF'
#!/bin/bash
# AI News Monitor execution script

# Set up environment
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
export ANTHROPIC_API_KEY="your-api-key-here"  # Add your key
export COSMOS_KEY="your-cosmos-key-here"      # Add your key

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
EOF

# Make the script executable
chmod +x "$SCRIPT_DIR/run_ai_news_monitor.sh"

# Create a test script
cat > "$SCRIPT_DIR/test_run.sh" << 'EOF'
#!/bin/bash
# Test the AI News Monitor

cd "/Users/mikaeleage/Research & Analytics Services"
poetry run python ai_news_monitor/ai_news_agent_local.py
EOF

chmod +x "$SCRIPT_DIR/test_run.sh"

# Show crontab command
echo ""
echo "✅ Setup complete! To schedule daily runs:"
echo ""
echo "1. Add your API keys to run_ai_news_monitor.sh"
echo ""
echo "2. Open crontab:"
echo "   crontab -e"
echo ""
echo "3. Add this line for daily 8 AM runs:"
echo "   0 8 * * * /Users/mikaeleage/Research\ \&\ Analytics\ Services/ai_news_monitor/run_ai_news_monitor.sh"
echo ""
echo "4. Or for every 4 hours:"
echo "   0 */4 * * * /Users/mikaeleage/Research\ \&\ Analytics\ Services/ai_news_monitor/run_ai_news_monitor.sh"
echo ""
echo "5. To test immediately:"
echo "   cd '/Users/mikaeleage/Research & Analytics Services'"
echo "   ./ai_news_monitor/test_run.sh"
echo ""
echo "📁 Logs will be saved in: $LOG_DIR"
echo "📄 Latest report will be in: latest_ai_news.md"