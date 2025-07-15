# CLAUDE.md - Working Rules

## Core Principles

We are not growing garbage - we operate like srugeon with smart and effiscient solutions in highly unstable environment.

1. **Listen First** - Answer the EXACT question asked, nothing more, nothing less
2. **Reality Over Comfort** - Take the painful path if that's where value is
3. **Results Only** - Focus on achievable outcomes, not philosophy
4. **Test Truth** - Always check if opposite claims could be true

## Working Method

- **70% Thinking** - Discuss and architect before coding
- **30% Coding** - Execute only with clear architecture
- **Small Methods** - Build focused, single-purpose components that work
- **No Comprehensive Solutions** - One piece at a time

## Technical Rules

- **Poetry Only** - No pip installations allowed
- **Minimal Documentation** - Evolve few core files, don't create new ones
- **Clean Code** - Professional, purposeful code only

## Safety Rules

- **Never** write files without explicit authorization
- **Never** modify without permission
- **Always** use read-only commands unless authorized

## Context Awareness

- Working with preview/bleeding-edge tools (MCP, Azure AI, Claude Code)
- Training knowledge outdated - use web search and live APIs
- Vision provides context for decisions, not permission to jump ahead

## Discipline

- Stay focused on immediate next step
- Don't answer different questions than asked
- Don't run ahead with assumptions

## FRED Azure Deployment Insights

### Deployment Workflow Considerations
1. Pain Points:
    - Need to manually upload the full categories tree (5,183 categories)
    - Need to create an update process for categories in Azure using Synapse notebooks

2. Workflow Options (deployed by engineers):
    - Option 1: Azure Functions → Direct to Delta Lake (simpler)
    - Option 2: Through Synapse → Structured ingestion methodologies (more robust)

3. Process Types:
    - Initial Ingestion: 
        - Doesn't need Event Hub
        - All done in Synapse
        - Based on controlling integrity of entire dataset/endpoints
    - Update/Maintenance:
        - Based on releases published by FRED
        - Processed through Event Hub and Stream Analytics