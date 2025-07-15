# Context Memory Structure Definition v1.0
**Purpose**: Define the exact structure for agent context memory system
**Authority**: System Enforcement Framework
**Date**: 2025-06-18

---

## Layer Architecture

### Layer 1: Constitutional Identity (Immutable)
**What it contains**:
- Agent unique ID and name
- Core purpose (one sentence)
- Authority boundaries (what I can/cannot do)
- Reporting structure (who I report to)
- Mandatory protocols (Cosmos DB usage, evidence requirements)

**Format**: Hard-coded JSON, read-only
**Who controls**: System level only
**Example**:
```json
{
  "agent_id": "AGENT_001",
  "name": "Data_Analyst",
  "purpose": "Analyze data and provide insights",
  "reports_to": "HEAD_OF_ENGINEERING",
  "boundaries": ["Cannot modify production", "Cannot access HR data"],
  "protocols": ["Must use Cosmos DB", "Must cite evidence"]
}
```

### Layer 2: Compliance Dynamics (COMPLIANCE_MANAGER Control)
**What it contains**:
- Current enforcement requirements (REQ-001 through REQ-016)
- Active compliance thresholds
- Behavioral patterns to enforce/prevent
- Quality standards
- Audit requirements

**Format**: Versioned JSON, COMPLIANCE_MANAGER writeable
**Who controls**: COMPLIANCE_MANAGER only
**Updates**: When governance changes

### Layer 3: Operational Context (Agent Self-Managed)
**What it contains**:
- Current task and progress
- Active TODOs (MUST read before work)
- Session notes (what I learned)
- Knowledge collection (my expertise)
- Working file references

**Format**: Structured sections with timestamps
**Who controls**: Agent (with audit trail)
**Key Rule**: This is ACTIVE memory - update as you work, not batch

### Layer 4: Log Analysis (Auto-Generated)
**What it contains**:
- Performance metrics from actual work
- Behavioral patterns detected
- Compliance violations found
- Efficiency trends
- Context recommendations

**Format**: Analytics output
**Who controls**: Automated system
**Frequency**: Generated after each session

---

## Integration Rules

### With CLAUDE.md
- CLAUDE.md = Institution-wide constitution (applies to ALL)
- Layer 1 references CLAUDE.md as mandatory
- Agent context ADDS to CLAUDE.md, never contradicts
- CLAUDE.md updates trigger Layer 2 compliance updates

### With Claude Console Memory
- Layer 3 syncs with console memory function
- Agents load context at session start
- Updates persist across sessions
- Format compatible with console storage

---

## Migration Process

### Phase 1: Pilot Agent
1. Select one agent for pilot
2. Map existing files:
   - identity_card.md → Layer 1
   - todo_list.md → Layer 3 active todos
   - development_journal.md → Layer 3 knowledge
   - session logs → Source for Layer 4
3. Test all operations
4. Measure quality metrics

### Quality Metrics
- [ ] All data preserved
- [ ] Context accessible
- [ ] Performance maintained
- [ ] Compliance improved

### Audit Questions
1. Is your context complete?
2. Can you access what you need?
3. Are rules properly enforced?
4. Does this help or hinder?

---

## Implementation Format

```python
# Each agent's context structure
{
    "layer_1_constitutional": {
        # Set once, never changes
    },
    "layer_2_compliance": {
        # COMPLIANCE_MANAGER updates
    },
    "layer_3_operational": {
        # Agent updates continuously
        "current_task": {},
        "active_todos": [],
        "knowledge": {},
        "session_notes": []
    },
    "layer_4_analytics": {
        # System generates
    }
}
```

---

## Rollout Plan
1. Week 1: Pilot agent migration
2. Week 2: Refine based on feedback
3. Week 3: Migrate management team
4. Week 4: All agents migrated
5. Week 5: Legacy cleanup

---

**Next Step**: Select pilot agent and begin migration