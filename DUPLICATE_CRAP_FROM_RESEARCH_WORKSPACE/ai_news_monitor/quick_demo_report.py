#!/usr/bin/env python3
"""
Quick demo report - shows what will be in your inbox
"""
import os
import json
from datetime import datetime, timezone
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_demo_report():
    """Create a demo report showing the format"""
    print("🚀 Creating Demo AI News Report")
    print("=" * 50)
    
    # Demo content (what would come from the AI checks)
    demo_summary = f"""# AI Industry Weekly Update - {datetime.now().strftime('%B %d, %Y')}

## 🎯 Key Highlights
• **Anthropic**: Claude 3.5 Sonnet continues to lead in reasoning benchmarks
• **OpenAI**: GPT-4o with improved multimodal capabilities 
• **Google**: Gemini Pro 1.5 offers 2M token context window
• **Microsoft**: Azure AI Foundry expands model catalog

## 📊 Industry Trends
• **Context Windows**: Race to longer context lengths (1M+ tokens)
• **Multimodal**: Enhanced image, audio, and video processing
• **Enterprise Focus**: Better safety, reliability, and deployment tools
• **Cost Optimization**: More efficient models for production use

## 💡 Recommendations
• **Evaluate longer context models** for our FRED data analysis
• **Test multimodal capabilities** for dashboard visual analysis  
• **Monitor pricing changes** for cost optimization routing
• **Review safety updates** for enterprise deployment standards"""

    demo_updates = [
        {
            "provider": "Anthropic (Claude)",
            "updates": "• Claude 3.5 Sonnet maintains top performance in reasoning\n• New API features for batch processing\n• Improved safety measures for enterprise use",
            "checked_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "provider": "OpenAI", 
            "updates": "• GPT-4o enhanced multimodal processing\n• API rate limit improvements\n• New fine-tuning capabilities announced",
            "checked_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "provider": "Google Gemini",
            "updates": "• Gemini Pro 1.5 with 2M context window\n• Vertex AI platform updates\n• New code generation features",
            "checked_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "provider": "Microsoft Azure AI",
            "updates": "• Azure AI Foundry model catalog expansion\n• New deployment options for enterprise\n• Cost optimization tools for AI workloads",
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Create report structure
    report = {
        "summary": demo_summary,
        "detailed_updates": demo_updates,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "providers_checked": 4,
        "demo_note": "This is a demo report showing the format you'll receive daily"
    }
    
    # Save to Cosmos DB
    print("💾 Saving demo report to Cosmos DB...")
    
    try:
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("system_inbox")
        
        message_id = f"ai-news-demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        message = {
            "id": message_id,
            "partitionKey": "AI_NEWS_MONITOR",
            "messageType": "AI_NEWS_DEMO_REPORT",
            "sender": {
                "name": "AI_NEWS_MONITOR",
                "role": "Automated Agent (Demo)"
            },
            "recipients": ["HEAD_OF_RESEARCH", "HEAD_OF_ENGINEERING"],
            "subject": f"🤖 [DEMO] AI Industry Weekly Update - {datetime.now().strftime('%B %d, %Y')}",
            "content": report,
            "priority": "NORMAL", 
            "status": "UNREAD",
            "metadata": {
                "category": "INTELLIGENCE",
                "subcategory": "INDUSTRY_UPDATES",
                "importance": 4,
                "tags": ["ai-news", "demo-report", "automated"],
                "source": "ai_news_monitor_demo",
                "demo": True
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
        
        container.create_item(body=message)
        
        print(f"✅ DEMO REPORT SAVED!")
        print(f"📧 Message ID: {message_id}")
        print(f"📮 Location: Cosmos DB > system_inbox")
        print(f"🏷️  Subject: [DEMO] AI Industry Weekly Update")
        
        # Show what the email looks like
        print(f"\n📧 EMAIL PREVIEW:")
        print("=" * 50)
        print(f"From: AI_NEWS_MONITOR")
        print(f"To: HEAD_OF_RESEARCH, HEAD_OF_ENGINEERING") 
        print(f"Subject: 🤖 [DEMO] AI Industry Weekly Update - {datetime.now().strftime('%B %d, %Y')}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print(demo_summary)
        print("=" * 50)
        
        # Save local copy
        with open("demo_ai_news_report.json", 'w') as f:
            json.dump(message, f, indent=2)
        
        print(f"\n💾 Local copy: demo_ai_news_report.json")
        
    except Exception as e:
        print(f"❌ Cosmos error: {e}")
        # Fallback to local save
        with open("demo_ai_news_fallback.json", 'w') as f:
            json.dump(report, f, indent=2)
        print(f"💾 Saved locally: demo_ai_news_fallback.json")
    
    print(f"\n🎉 DEMO COMPLETE!")
    print(f"📧 Check your Cosmos DB system_inbox for the demo email")
    print(f"🔄 This format will arrive daily at 8 AM once you set up cron")

if __name__ == "__main__":
    create_demo_report()