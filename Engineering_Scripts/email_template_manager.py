#!/usr/bin/env python3
"""
Email Template Manager for Azure Automated Email System
Manages templates for hourly/scheduled emails to managers and staff
"""

import os
import sys
from datetime import datetime, timedelta
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cosmos_db_manager import CosmosDBManager

class EmailTemplateManager:
    def __init__(self):
        self.db_manager = CosmosDBManager()
        self.database = self.db_manager.database
        
        # Create email_templates container if needed
        self.templates_container = self.ensure_container('email_templates', '/template_type')
        self.email_queue_container = self.ensure_container('email_queue', '/priority')
        self.email_responses_container = self.ensure_container('email_responses', '/request_id')
        self.quality_reports_container = self.ensure_container('quality_reports', '/report_type')
    
    def ensure_container(self, container_name, partition_key):
        """Ensure container exists"""
        try:
            container = self.database.create_container(
                id=container_name,
                partition_key={'paths': [partition_key], 'kind': 'Hash'}
            )
            print(f"✅ Created '{container_name}' container")
            return container
        except Exception as e:
            if "already exists" in str(e):
                print(f"⚠️  '{container_name}' container already exists")
                return self.database.get_container_client(container_name)
            raise e
    
    def create_email_templates(self):
        """Create standard email templates for automated sending"""
        
        templates = [
            {
                "id": "template_log_collection_request",
                "template_type": "LOG_COLLECTION",
                "name": "Agent Log Collection Request",
                "subject": "🚨 HIGH PRIORITY: Submit Session Logs - Response Required Within 1 Hour",
                "priority": "HIGH",
                "frequency": "hourly",
                "recipients": ["All-Agents"],
                "body": """# HIGH PRIORITY: Session Log Submission Required

**Response Deadline**: Within 1 hour of receipt
**Priority Level**: HIGH
**Automated Reminder**: Will be sent if no response

## Required Actions:

1. **Submit today's session log** to the logs container
2. **Include evidence** for all actions taken (command + output)
3. **Update your todo list** with current status
4. **Report any blockers** or issues encountered

## Submission Format:
```json
{
    "agent_id": "YOUR_AGENT_NAME",
    "session_date": "YYYY-MM-DD",
    "log_path": "/path/to/session_log.md",
    "tasks_completed": ["task1", "task2"],
    "blockers": ["blocker1"],
    "evidence_provided": true
}
```

## Compliance Notice:
- Failure to respond within 1 hour will trigger escalation
- Incomplete logs will be flagged for quality review
- Pattern violations will be automatically reported

**This is an automated high-priority request. Response required.**
""",
                "response_required": True,
                "response_deadline_hours": 1,
                "escalation_enabled": True,
                "quality_check_enabled": True
            },
            
            {
                "id": "template_task_completion_verification",
                "template_type": "TASK_VERIFICATION",
                "name": "Task Completion Verification Request",
                "subject": "🔍 VERIFICATION REQUIRED: Confirm Task Completion with Evidence",
                "priority": "HIGH",
                "frequency": "on_completion_claim",
                "recipients": ["{{agent_id}}"],
                "body": """# Task Completion Verification Required

**Task ID**: {{task_id}}
**Claimed Completion**: {{completion_timestamp}}
**Verification Deadline**: 30 minutes

## You claimed completion of: "{{task_description}}"

### Required Evidence:
1. **Output/Results**: Provide actual output or screenshots
2. **File References**: List all files created/modified with line numbers
3. **Test Results**: Show tests passing or validation results
4. **Query Results**: If data-related, show actual query results

### Verification Checklist:
- [ ] Task output matches expected results
- [ ] All acceptance criteria met
- [ ] Evidence provided in filepath:line format
- [ ] No mock/placeholder data used
- [ ] Changes tested and verified

### Submit Evidence:
```json
{
    "task_id": "{{task_id}}",
    "evidence_type": "completion_verification",
    "outputs": {
        "files_created": ["file1:lines", "file2:lines"],
        "test_results": "actual test output here",
        "query_results": "actual data here",
        "screenshots": ["path/to/screenshot1.png"]
    },
    "verification_statement": "I verify this task is 100% complete"
}
```

**Unverified completions will be marked as INCOMPLETE.**
""",
                "response_required": True,
                "response_deadline_minutes": 30,
                "escalation_enabled": True,
                "auto_incomplete_on_timeout": True
            },
            
            {
                "id": "template_initialization_compliance_check",
                "template_type": "COMPLIANCE_CHECK",
                "name": "8-Step Initialization Compliance Check",
                "subject": "⚠️ COMPLIANCE CHECK: Initialization Protocol Verification",
                "priority": "CRITICAL",
                "frequency": "daily",
                "recipients": ["All-Agents"],
                "body": """# Mandatory Initialization Protocol Compliance Check

**Compliance Deadline**: 15 minutes
**Non-compliance Result**: Agent lockdown

## Verify 8-Step Initialization Completed Today:

1. ✓ Environment verification (pwd check)
2. ✓ Read last 20 lines of /Inbox/ledger.md
3. ✓ Located identity prompt
4. ✓ Verified 8-file agent package
5. ✓ Created today's session log
6. ✓ Updated todo list
7. ✓ Sent initialization heartbeat
8. ✓ Understood three-pillar governance

## Submit Compliance Proof:
```json
{
    "agent_id": "YOUR_AGENT_NAME",
    "initialization_timestamp": "YYYY-MM-DD HH:MM:SS",
    "session_log_path": "/path/to/logs/session_YYYY-MM-DD.md",
    "heartbeat_message_id": "message_id",
    "pwd_result": "/correct/workspace/path",
    "all_steps_completed": true
}
```

**Failure to provide evidence = PROTOCOL VIOLATION**
""",
                "response_required": True,
                "response_deadline_minutes": 15,
                "violation_on_timeout": True,
                "auto_lockdown_enabled": True
            },
            
            {
                "id": "template_manager_status_update",
                "template_type": "STATUS_UPDATE",
                "name": "Manager Status Update Request",
                "subject": "📊 MANAGER UPDATE REQUIRED: Team Status and Blockers",
                "priority": "HIGH",
                "frequency": "twice_daily",
                "recipients": ["HEAD_OF_ENGINEERING", "HEAD_OF_RESEARCH", "HEAD_OF_DIGITAL_STAFF", "COMPLIANCE_MANAGER"],
                "body": """# Manager Status Update Required

**Update Deadline**: 2 hours
**Format**: Structured JSON response required

## Required Information:

### 1. Team Status Overview
- Active agents and their current tasks
- Completed work since last update
- Blockers and issues requiring attention

### 2. Compliance Metrics
- Initialization compliance rate
- Task completion rate with evidence
- Violation patterns observed

### 3. Resource Needs
- Additional support required
- Process improvements needed
- Escalations for executive attention

## Response Format:
```json
{
    "manager_id": "YOUR_MANAGER_ID",
    "reporting_period": "YYYY-MM-DD HH:MM to YYYY-MM-DD HH:MM",
    "team_status": {
        "active_agents": 5,
        "tasks_in_progress": 12,
        "tasks_completed": 8,
        "compliance_rate": 0.85
    },
    "blockers": [
        {
            "agent": "agent_name",
            "issue": "description",
            "impact": "HIGH|MEDIUM|LOW",
            "resolution_needed": "what's needed"
        }
    ],
    "escalations": [],
    "quality_score": 0.9
}
```

**This update feeds executive dashboards. Accuracy required.**
""",
                "response_required": True,
                "response_deadline_hours": 2,
                "dashboard_integration": True,
                "executive_visibility": True
            },
            
            {
                "id": "template_reminder_first",
                "template_type": "REMINDER",
                "name": "First Reminder - Response Required",
                "subject": "⏰ REMINDER: Response Required - {{original_subject}}",
                "priority": "URGENT",
                "frequency": "as_needed",
                "recipients": ["{{original_recipient}}"],
                "body": """# REMINDER: Immediate Response Required

**Original Request**: {{original_subject}}
**Sent**: {{original_timestamp}}
**Deadline**: {{deadline_timestamp}}
**Time Remaining**: {{time_remaining}}

## You have not responded to the high-priority request.

### Original Request Summary:
{{original_request_summary}}

### Why This Matters:
- Automated escalation will occur if no response
- Compliance tracking affected
- Team metrics impacted

### Quick Response Option:
If you need more time, reply with:
```json
{
    "request_id": "{{request_id}}",
    "status": "acknowledged",
    "estimated_completion": "YYYY-MM-DD HH:MM",
    "reason_for_delay": "brief explanation"
}
```

**Second reminder will include manager escalation.**
""",
                "response_required": True,
                "is_reminder": True,
                "escalation_warning": True
            },
            
            {
                "id": "template_quality_feedback",
                "template_type": "QUALITY_FEEDBACK",
                "name": "Response Quality Feedback",
                "subject": "📋 Quality Review: Your Response Requires Improvement",
                "priority": "MEDIUM",
                "frequency": "as_needed",
                "recipients": ["{{agent_id}}"],
                "body": """# Response Quality Review

**Your Response ID**: {{response_id}}
**Quality Score**: {{quality_score}}/100
**Status**: REQUIRES IMPROVEMENT

## Issues Identified:

{{quality_issues}}

## Required Corrections:

1. **Missing Evidence**: 
   - Expected: {{expected_evidence}}
   - Provided: {{provided_evidence}}

2. **Format Compliance**:
   - Required format not followed
   - Missing required fields

3. **Completeness**:
   - {{completeness_percentage}}% complete
   - Missing: {{missing_elements}}

## Resubmission Required:
Please resubmit with corrections within 1 hour.

### Quality Standards Reminder:
- All claims require filepath:line evidence
- No mock or placeholder data
- Complete responses only
- Follow specified format exactly

**Pattern violations will trigger compliance review.**
""",
                "response_required": True,
                "response_deadline_hours": 1,
                "quality_tracking": True,
                "pattern_detection": True
            }
        ]
        
        # Save templates to container
        saved_count = 0
        for template in templates:
            try:
                self.templates_container.create_item(template)
                saved_count += 1
                print(f"✅ Created template: {template['name']}")
            except Exception as e:
                if "already exists" in str(e):
                    # Update existing template
                    self.templates_container.upsert_item(template)
                    print(f"📝 Updated template: {template['name']}")
                else:
                    print(f"❌ Error with template {template['name']}: {e}")
        
        print(f"\n✅ Email templates ready: {len(templates)} templates configured")
        return templates
    
    def create_automation_config(self):
        """Create Azure Automation configuration"""
        
        automation_config = {
            "id": "email_automation_config",
            "schedules": [
                {
                    "name": "hourly_log_collection",
                    "template_id": "template_log_collection_request",
                    "frequency": "0 * * * *",  # Every hour
                    "enabled": True,
                    "recipient_groups": ["All-Agents"]
                },
                {
                    "name": "daily_compliance_check",
                    "template_id": "template_initialization_compliance_check",
                    "frequency": "0 9 * * *",  # 9 AM daily
                    "enabled": True,
                    "recipient_groups": ["All-Agents"]
                },
                {
                    "name": "manager_updates",
                    "template_id": "template_manager_status_update",
                    "frequency": "0 9,17 * * *",  # 9 AM and 5 PM
                    "enabled": True,
                    "recipient_groups": ["All-Managers"]
                }
            ],
            "reminder_rules": {
                "first_reminder": {
                    "delay_minutes": 30,
                    "template_id": "template_reminder_first"
                },
                "second_reminder": {
                    "delay_minutes": 50,
                    "include_manager": True,
                    "escalation": True
                },
                "final_escalation": {
                    "delay_minutes": 65,
                    "auto_violation_report": True
                }
            },
            "quality_thresholds": {
                "minimum_score": 70,
                "evidence_required": True,
                "format_compliance": True,
                "completeness_required": 0.9
            },
            "response_tracking": {
                "container": "email_responses",
                "quality_analysis_enabled": True,
                "pattern_detection": True,
                "auto_reports": True
            }
        }
        
        # Save configuration
        config_path = Path("/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/automation/email_automation_config.json")
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(automation_config, f, indent=2)
        
        print(f"✅ Automation configuration saved to: {config_path}")
        return automation_config
    
    def create_response_controller(self):
        """Create controller logic for checking responses"""
        
        controller_logic = """
# Email Response Controller Logic

## Phase 1: Response Collection (Every 15 minutes)
1. Check email_queue for sent emails
2. Match responses in email_responses container
3. Track response rate and timing

## Phase 2: Reminder Triggering (Every 30 minutes)
1. Identify non-responders
2. Check reminder rules
3. Queue reminder emails with escalation level

## Phase 3: Quality Analysis (Every hour)
1. Analyze response quality:
   - Evidence provided?
   - Format compliance?
   - Completeness check?
2. Generate quality scores
3. Queue feedback emails for low scores

## Phase 4: Report Generation (Every 2 hours)
1. Compile response metrics
2. Identify patterns and repeat offenders
3. Create quality report in quality_reports container
4. Flag for Claude Code review

## Escalation Matrix:
- No response in 30 min → First reminder
- No response in 50 min → Manager CC'd
- No response in 65 min → Violation report
- Low quality pattern → Compliance review
"""
        
        controller_path = Path("/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/automation/response_controller_logic.md")
        with open(controller_path, 'w') as f:
            f.write(controller_logic)
        
        print(f"✅ Controller logic saved to: {controller_path}")
        return controller_logic

def main():
    """Initialize email template system"""
    manager = EmailTemplateManager()
    
    print("🚀 INITIALIZING EMAIL TEMPLATE MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Create templates
    templates = manager.create_email_templates()
    
    # Create automation config
    config = manager.create_automation_config()
    
    # Create controller logic
    controller = manager.create_response_controller()
    
    print("\n✅ EMAIL AUTOMATION SYSTEM READY")
    print("=" * 60)
    print("\nContainers Created:")
    print("  - email_templates (6 templates)")
    print("  - email_queue (for outgoing emails)")
    print("  - email_responses (for tracking responses)")
    print("  - quality_reports (for analysis reports)")
    print("\nAutomation Features:")
    print("  - Hourly log collection requests")
    print("  - Daily compliance checks")
    print("  - Automated reminders with escalation")
    print("  - Quality analysis and feedback")
    print("  - Manager status updates")
    print("\n🎯 Next Steps:")
    print("1. Configure Azure Logic Apps with these templates")
    print("2. Set up response controllers")
    print("3. Enable quality analysis automation")
    print("4. Test with pilot group")

if __name__ == "__main__":
    main()