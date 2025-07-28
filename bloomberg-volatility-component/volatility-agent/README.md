# Autonomous Volatility Trading Agent

An LLM-powered autonomous agent that monitors FX volatility markets, makes trading decisions, and learns from outcomes.

## Key Features

- **LLM Reasoning**: Uses Claude to reason about market conditions and make decisions
- **Autonomous Operation**: Runs continuously, making decisions without human intervention
- **Market Analysis**: Fetches and analyzes Bloomberg volatility surface information
- **Learning System**: Tracks performance and learns from successes/failures
- **State Persistence**: Maintains state between runs

## Architecture

```
Agent Loop:
1. Get Market Context
2. Ask Claude for Decision (with full reasoning)
3. Execute Decision
4. Learn from Outcome
5. Save State
6. Wait and Repeat
```

## Setup

1. Copy `.env.example` to `.env` and add your Anthropic API key:
```bash
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

2. Install dependencies:
```bash
npm install
```

3. Run the agent:
```bash
npm run agent
```

## Agent Actions

The agent can autonomously decide to:
- `FETCH_VOLATILITY`: Get latest Bloomberg information
- `ANALYZE_REGIME`: Determine current market regime
- `RECOMMEND_POSITION`: Generate trade ideas
- `UPDATE_POSITIONS`: Manage existing positions
- `WAIT`: Observe without action

## State Management

Agent state is persisted in `./state/agent_state.json` including:
- Last analysis results
- Current market regime assessment
- Open positions
- Performance history
- Learned observations

## Monitoring

The agent logs all decisions and reasoning to console. Key events:
- 🤖 Agent starting
- 🔄 Cycle beginning
- 🧠 Claude reasoning
- 🚀 Action execution
- ✅ Success
- ❌ Errors

## Configuration

Environment variables:
- `ANTHROPIC_API_KEY`: Your Claude API key (required)
- `BLOOMBERG_API_URL`: Bloomberg API endpoint
- `AGENT_RUN_INTERVAL`: Milliseconds between cycles (default: 60000)
- `AGENT_STATE_FILE`: Path to state file

## Safety Features

- Graceful shutdown on SIGINT
- Error recovery with Claude reasoning
- State persistence between runs
- Confidence scoring on decisions

## Running the Agent

The agent requires:
1. Valid Anthropic API key
2. Access to Bloomberg API
3. Node.js 18+ installed

Start with: `npm run agent`