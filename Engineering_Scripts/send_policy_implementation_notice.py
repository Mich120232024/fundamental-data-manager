#!/usr/bin/env python3
"""
Send policy implementation notice to management team
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Load environment
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Import cosmos manager
sys.path.insert(0, str(Path(__file__).parent))
from cosmos_db_manager import get_db_manager

def create_policy_notice():
    """Create policy implementation notice"""
    
    message_content = """Management Team,

Following the successful establishment of our Cosmos DB infrastructure (677 messages, 5 containers operational), we are implementing Enhanced Semantic Policy v2.0 for organizational consistency.

**INFRASTRUCTURE STATUS:**
✅ Messages Container: 677 communications tracked
✅ Documents Container: Governance migration complete  
✅ Processes Container: Operational procedures active
✅ Institutional Data Center: Research library ready
✅ Enhanced Semantic Policy: Team-specific guidelines deployed

**IMPLEMENTATION REQUIREMENTS:**

**Core Naming Convention (All Teams):**
Pattern: {type}-{category}-{identifier}_{name}
Example: report-governance-q2-2025_compliance_analysis

**Required Tags (Universal):**
- type: document type
- category: business category  
- status: current status
- owner: responsible party
- audience: intended users

**Team-Specific Optional Tags:**
- Engineering: complexity, dependencies, test_coverage
- Governance: compliance_level, evidence_required, audit_frequency
- Research: methodology, confidence_level, peer_reviewed
- Business: roi_impact, stakeholders, market_segment
- Executive: strategic_priority, decision_impact, board_visibility
- Digital Labor: skill_level, utilization_rate, performance_tier

**ACTION ITEMS:**

1. **All Managers**: Review policy with teams, apply to new documents
2. **COMPLIANCE_MANAGER**: Update all procedures including agent onboarding templates to reflect new policy
3. **Document Creators**: Follow naming convention and tagging requirements
4. **Team Leads**: Ensure team members understand their optional tags

**BENEFITS:**
- Instant document discovery via database queries
- Cross-team collaboration improvement
- Governance compliance tracking
- Analytics and reporting capabilities

**IMPLEMENTATION:**
Policy is available in metadata container at `/metadata_container/enhanced_semantic_policy.json`

**COMPLIANCE:**
Please confirm receipt and implementation timeline with your teams.

The infrastructure transformation from file-based to database-driven documentation enables organizational intelligence and efficiency improvements.

Best regards,
Infrastructure Management"""

    return message_content

def send_to_managers():
    """Send implementation notice to all managers"""
    
    db = get_db_manager()
    messages_container = db.database.get_container_client('system_inbox')
    
    managers = [
        'HEAD_OF_ENGINEERING',
        'HEAD_OF_RESEARCH', 
        'HEAD_OF_DIGITAL_STAFF',
        'COMPLIANCE_MANAGER',
        'Management_Team'
    ]
    
    content = create_policy_notice()
    timestamp = datetime.now().isoformat() + 'Z'
    
    sent_messages = []
    
    for manager in managers:
        message_id = f"msg_{timestamp}_{hash(manager + timestamp) % 10000:04d}"
        
        message = {
            'id': message_id,
            'partitionKey': '2025-06',
            'timestamp': timestamp,
            'from': 'HEAD_OF_ENGINEERING',
            'to': manager,
            'subject': 'Enhanced Semantic Policy v2.0 - Implementation Notice',
            'content': content,
            'priority': 'high',
            'requiresResponse': True,
            'type': 'POLICY_IMPLEMENTATION',
            'status': 'sent',
            'tags': ['policy', 'implementation', 'semantic', 'infrastructure']
        }
        
        try:
            result = messages_container.create_item(message)
            sent_messages.append(manager)
            print(f"✅ Sent to {manager}: {message_id}")
            
        except Exception as e:
            print(f"❌ Failed to send to {manager}: {e}")
    
    return sent_messages

def main():
    """Main execution"""
    
    print("📧 SENDING ENHANCED SEMANTIC POLICY IMPLEMENTATION NOTICE")
    print("="*60)
    
    sent = send_to_managers()
    
    print(f"\n✅ Policy implementation notice sent to {len(sent)} managers:")
    for manager in sent:
        print(f"   • {manager}")
    
    print(f"\n📋 KEY REQUESTS:")
    print("   • All managers: Review and implement with teams")
    print("   • COMPLIANCE_MANAGER: Update procedures and agent templates")
    print("   • Teams: Apply policy to new documents")
    
    print(f"\n🎯 Expected Outcomes:")
    print("   • Consistent document naming across organization")
    print("   • Improved searchability via database queries")
    print("   • Enhanced cross-team collaboration")
    print("   • Governance compliance tracking")

if __name__ == "__main__":
    main()