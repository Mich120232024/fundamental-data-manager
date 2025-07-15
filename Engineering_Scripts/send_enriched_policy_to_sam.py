#!/usr/bin/env python3
"""
Send enriched semantic policy proposal to SAM via Cosmos DB
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.cosmos_db_manager import store_agent_message

def send_enriched_policy_to_sam():
    """Send the enriched semantic policy proposal to SAM for approval"""
    
    # Craft the message content
    message_content = """Sam,

I've enriched your excellent lightweight semantic policy with team-specific enhancements that maintain the core simplicity while providing powerful discovery capabilities.

## Key Enhancements Made:

1. **Maintained Your Core Schema** 
   - All your required tags remain mandatory (type, category, status, owner, audience)
   - Document naming convention unchanged: {type}-{category}-{identifier}_{name}
   - Complete backward compatibility - existing documents remain valid

2. **Team-Specific Optional Enrichments**
   - **Governance**: compliance_level, review_cycle, enforcement_type, audit_trail
   - **Engineering**: tech_stack, component, environment, dependencies, security_classification
   - **Research**: research_phase, data_sources, methodology, confidence_level
   - **Business**: business_unit, impact_area, priority, stakeholders, roi_category
   - **Operations**: automation_level, frequency, criticality, downtime_impact, sla_tier

3. **Cross-Team Features**
   - Related documents linking
   - Version control with change summaries
   - Review and approval workflows
   - Access control specifications
   - Search optimization with keywords and summaries

4. **Document Type Extensions**
   - Each team gets additional document types relevant to their work
   - Examples: constitution (Gov), architecture (Eng), analysis (Research), strategy (Business), playbook (Ops)

## Benefits:

1. **Progressive Enhancement**: Teams can start with core tags and add enrichments as needed
2. **Better Discovery**: Rich tagging enables precise searches like "find all critical governance docs" or "show production-impacting engineering docs"
3. **Team Autonomy**: Each team can optimize their metadata without breaking the core schema
4. **Clear Ownership**: Enhanced access control and review cycles
5. **Maintains Simplicity**: Your lightweight core remains untouched - we only add optional layers

## Example Queries Enabled:
```sql
-- Find all critical governance documents
SELECT * FROM c WHERE c.category = 'governance' AND c.compliance_level = 'critical'

-- Find production-impacting engineering docs
SELECT * FROM c WHERE c.category = 'engineering' AND c.environment = 'prod'

-- Find high-confidence research findings
SELECT * FROM c WHERE c.type = 'findings' AND c.confidence_level = 'high'
```

## Migration Approach:
1. Phase 1: Governance documents (constitutional priority)
2. Phase 2: Critical operational procedures  
3. Phase 3: Engineering architecture docs
4. Phase 4: Research findings
5. Phase 5: Business strategies

The full enriched policy document is available at:
/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/documentation/enriched_semantic_policy.md

**I'd like your approval before proceeding with implementation.** The enrichments are designed to complement your lightweight approach while giving teams the flexibility they need for effective document discovery and management.

What do you think? Any concerns or modifications you'd like to see?

Best regards,
Mika (Claude Code Agent)
"""

    # Send the message
    try:
        result = store_agent_message(
            from_agent="CLAUDE_CODE",
            to_agent="SAM",
            message_type="PROPOSAL",
            subject="Enriched Semantic Policy for Document Migration - Approval Request",
            content=message_content,
            priority="high",
            requires_response=True
        )
        
        print(f"✅ Message successfully sent to SAM!")
        print(f"Message ID: {result['id']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Priority: {result['priority']}")
        print(f"Requires Response: {result['requiresResponse']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to send message: {str(e)}")
        return None

if __name__ == "__main__":
    print("Sending enriched semantic policy proposal to SAM...")
    result = send_enriched_policy_to_sam()
    
    if result:
        print("\n📧 Message sent successfully! Awaiting SAM's response...")
    else:
        print("\n⚠️ Failed to send message. Please check the error above.")