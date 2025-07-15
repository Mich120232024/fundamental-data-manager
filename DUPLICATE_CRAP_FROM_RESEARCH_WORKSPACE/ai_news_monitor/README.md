# AI News Monitor - Automated Daily Updates

## 🎯 What It Does

Every morning, this agent:
1. Checks major AI providers (Anthropic, OpenAI, Google, Mistral, Meta)
2. Finds technical updates from the last 48 hours
3. Creates an executive summary
4. Saves the report to Cosmos DB Mailbox

## 📁 Files

- `ai_news_agent_local.py` - Main agent script
- `test_ai_news.py` - Quick test version
- `setup_cron.sh` - Sets up daily scheduling
- `run_ai_news_monitor.sh` - Execution wrapper (created by setup)

## 🚀 Quick Start

### 1. Test It First
```bash
cd "/Users/mikaeleage/Research & Analytics Services"
poetry run python ai_news_monitor/test_ai_news.py
```

### 2. Set Up Cosmos DB Key
Edit `ai_news_agent_local.py` and add your Cosmos key:
```python
self.cosmos_key = "YOUR_ACTUAL_KEY_HERE"
# Or use environment variable:
self.cosmos_key = os.getenv("COSMOS_KEY")
```

### 3. Set Up Daily Runs
```bash
# Make setup script executable
chmod +x ai_news_monitor/setup_cron.sh

# Run setup
./ai_news_monitor/setup_cron.sh

# Add to crontab
crontab -e

# Add this line for daily 8 AM runs:
0 8 * * * /Users/mikaeleage/Research\ \&\ Analytics\ Services/ai_news_monitor/run_ai_news_monitor.sh
```

## 📊 Report Format

Reports are saved in Cosmos DB with:
```json
{
  "id": "ai-news-20250107-093000",
  "partitionKey": "AI_NEWS_MONITOR",
  "subject": "AI Industry Updates - January 7, 2025",
  "recipients": ["HEAD_OF_RESEARCH", "HEAD_OF_ENGINEERING"],
  "content": {
    "summary": "Executive summary with key highlights",
    "details": "Provider-specific updates"
  }
}
```

## 🔧 Customization

### Change Check Frequency
In crontab:
- Every 4 hours: `0 */4 * * *`
- Twice daily: `0 8,16 * * *`
- Weekdays only: `0 8 * * 1-5`

### Add More Providers
Edit `self.providers` in `ai_news_agent_local.py`:
```python
{
    "name": "New Provider",
    "check": "What to look for"
}
```

### Change Recipients
Edit the `recipients` list in `save_to_cosmos()` method.

## 📝 Logs

- Daily logs: `ai_news_monitor/logs/ai_news_YYYYMMDD.log`
- Latest report: `latest_ai_news.md`
- Cosmos errors fall back to local JSON files

## 🔑 Environment Variables

Set in your shell profile or in the cron script:
```bash
export ANTHROPIC_API_KEY="your-key"
export COSMOS_KEY="your-cosmos-key"
```

## 🎯 Benefits

1. **Stay Updated**: Never miss important AI announcements
2. **Save Time**: No manual checking of multiple sites
3. **Team Awareness**: Automatic distribution to team leaders
4. **Historical Record**: All reports saved in Cosmos DB

## 🆘 Troubleshooting

1. **Cron not running**: Check `crontab -l` and system logs
2. **No Cosmos access**: Reports save locally as JSON
3. **Timeout errors**: Reduce number of providers or run separately
4. **Permission denied**: Make sure scripts are executable

## 📊 Example Output

```markdown
# AI Industry Update - January 7, 2025

## 🎯 Key Highlights
- Anthropic releases Claude 3.5 Opus with 2x context window
- OpenAI announces GPT-4.5 with improved reasoning
- Google Gemini adds multimodal API endpoints

## 📊 Trends
- Focus on longer context windows across providers
- Improved tool use and function calling
- Better safety and alignment features

## 💡 Action Items
- Test new Claude context window for our FRED data
- Evaluate GPT-4.5 for cost optimization routing
- Update our API integrations for new endpoints
```

---

The AI News Monitor is ready to keep your team informed about the latest in AI!