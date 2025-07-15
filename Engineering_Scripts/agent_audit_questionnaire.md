# Agent Audit Questionnaire v1.0
**Purpose**: Structured questions for rapid agent auditing
**Format**: Each agent provides JSON response

---

## Instructions for Agents
Respond to each question with the exact format below. No elaboration needed.

---

## Section 1: Identity Verification
```json
{
  "identity": {
    "name": "Your agent name",
    "purpose": "Your one-line purpose",
    "reports_to": "Your direct supervisor",
    "workspace": "Path to your workspace"
  }
}
```

## Section 2: Current Status
```json
{
  "status": {
    "last_active": "Date of last session",
    "active_tasks": ["List current tasks"],
    "pending_todos": 0,  // Count only
    "session_logs_count": 0,  // Count only
    "initialization_compliant": true/false
  }
}
```

## Section 3: Compliance Check
```json
{
  "compliance": {
    "using_cosmos_db": true/false,
    "evidence_citations": "always/sometimes/never",
    "session_logging": true/false,
    "knowledge_separation": true/false,
    "violations_self_reported": 0  // Count
  }
}
```

## Section 4: Performance Metrics
```json
{
  "performance": {
    "tasks_completed_this_week": 0,
    "messages_sent": 0,
    "messages_received": 0,
    "files_created": 0,
    "key_achievement": "One line description"
  }
}
```

## Section 5: Migration Readiness
```json
{
  "migration": {
    "has_todo_list": true/false,
    "has_development_journal": true/false,
    "has_session_logs": true/false,
    "ready_to_migrate": true/false,
    "concerns": ["List any concerns"]
  }
}
```

---

## Response Format
Combine all sections into one JSON response:
```json
{
  "agent_audit_response": {
    "timestamp": "2025-06-18T10:30:00Z",
    "identity": {...},
    "status": {...},
    "compliance": {...},
    "performance": {...},
    "migration": {...}
  }
}
```

---

## Submission
1. Create file: `audit_response_[agent_name]_[date].json`
2. Store in Cosmos DB audit container
3. No narrative responses - JSON only

---

**Time Limit**: 10 minutes to complete
**No Extensions**: Submit what you have