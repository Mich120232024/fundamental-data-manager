# Debug Analysis: /become Command

## Current Behavior
When running `/become software_agent bloomberg_api`, Claude:
1. Looks for agent information
2. Finds richer content in old Research & Analytics workspace
3. Uses that instead of new GZC Intel Workspace

## Root Cause
- Old workspace: Extensive files (MASTERPROMPT.md, BEHAVIOR_ADJUSTMENT_PROMPT.md, etc.)
- New workspace: Only basic identity.md
- Claude naturally gravitates to more detailed information

## Solution Options

### Option 1: Explicit Workspace Direction
Update /become command to explicitly state:
```
Use ONLY files from /Users/mikaeleage/GZC Intel Workspace/
DO NOT read from Research & Analytics Services
```

### Option 2: Enrich New Workspace
Add minimal but sufficient content to new workspace:
- Enhanced identity.md with concrete rules
- Link to project context
- Rely on hooks for persistence

### Option 3: Hook-First Approach  
Make the hook system primary:
1. /become sets ~/.claude/current_agent.txt
2. Hook injects full identity on EVERY prompt
3. No need to read many files

## Recommended Approach
**Option 3** - Hook-first is cleanest because:
- No file duplication
- Identity persists automatically
- Works with any workspace structure
- Already configured in settings.json

## Test Plan
1. Set agent: `echo "SOFTWARE_AGENT_001" > ~/.claude/current_agent.txt`
2. Test hook: `echo '{"prompt":"test"}' | python3 /path/to/hook`
3. Verify identity injection works
4. Update /become to just set agent state