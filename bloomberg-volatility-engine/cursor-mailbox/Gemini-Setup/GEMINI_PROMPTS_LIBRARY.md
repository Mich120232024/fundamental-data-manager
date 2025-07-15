# Gemini Prompts Library for Bloomberg Development

This library contains tested prompts that work well with Gemini CLI for Bloomberg Terminal integration tasks.

## 📊 Data Analysis Prompts

### Volatility Surface Analysis
```
I have Bloomberg FX volatility data:
[PASTE DATA HERE]

As a quantitative analyst, provide:
1. Market sentiment interpretation from risk reversals
2. Volatility smile shape analysis from butterflies  
3. Term structure insights
4. Statistical anomalies with confidence levels
5. Specific trading strategies with entry/exit points
```

### Market Data Discrepancy Analysis
```
Bloomberg Terminal shows: [TERMINAL VALUES]
API returns: [API VALUES]
Time difference: [MINUTES]

Analyze:
1. Technical reasons for discrepancies
2. Which source is more reliable and why
3. Code to detect and handle such differences
4. Business impact of using wrong values
```

### Real-time Data Quality Check
```
Evaluate this streaming Bloomberg data for quality issues:
[PASTE JSON DATA]

Check for:
1. Missing values or fields
2. Timestamp consistency
3. Price/volume anomalies
4. Cross-asset correlations
5. Data freshness indicators

Output a quality score and specific issues found.
```

## 💻 Code Generation Prompts

### React Component with Bloomberg Data
```
Create a production-ready React TypeScript component that:

Component Name: [NAME]
Data Source: Bloomberg API at /api/market-data
Update Frequency: [SECONDS]

Requirements:
1. Fetch these securities: [LIST SECURITIES]
2. Display as: [TABLE/CHART/SURFACE]
3. Error handling with exponential backoff
4. Loading skeleton screens
5. Responsive Tailwind CSS design
6. Unit tests with React Testing Library
7. Performance optimized with React.memo

Include all imports, types, and make it immediately usable.
```

### Python Bloomberg Client
```
Generate a Python class for Bloomberg Terminal integration:

Class Name: BloombergVolatilityClient
API Endpoint: http://20.172.249.92:8080
Python Version: 3.11

Features:
1. Async/await support
2. Connection pooling
3. Automatic retries with backoff
4. Data validation with pydantic
5. Caching with TTL
6. Comprehensive logging
7. Type hints throughout
8. Export to pandas DataFrame

Include docstrings and example usage.
```

### WebSocket Real-time Handler
```
Create a TypeScript WebSocket handler for Bloomberg real-time data:

WebSocket URL: ws://20.172.249.92:8080/stream
Data Format: { security: string, fields: { [key: string]: number }, timestamp: number }

Implement:
1. Auto-reconnection logic
2. Message queue for offline handling
3. Heartbeat/ping-pong
4. Error recovery
5. TypeScript interfaces
6. React hook wrapper
7. Subscription management

Make it production-ready with tests.
```

## 🐛 Debugging Prompts

### React Performance Issues
```
My React component is slow:
[PASTE COMPONENT CODE]

It updates every [FREQUENCY] with [DATA SIZE] data points.

Analyze and provide:
1. Specific performance bottlenecks with line numbers
2. React DevTools profiler interpretation
3. Optimization techniques (memo, callbacks, refs)
4. Refactored code with improvements
5. Before/after performance metrics
```

### API Integration Errors
```
Error: [PASTE ERROR MESSAGE]
Code: [PASTE RELEVANT CODE]
Context: Fetching Bloomberg data in [ENVIRONMENT]

Debug:
1. Root cause analysis
2. Step-by-step fix
3. Preventive measures
4. Error handling improvements
5. Logging additions for future debugging
```

### Data Inconsistency Issues
```
Expected data structure:
[PASTE EXPECTED FORMAT]

Actual data received:
[PASTE ACTUAL DATA]

Transformation code:
[PASTE YOUR CODE]

Fix the transformation and handle edge cases.
```

## 🏗️ Architecture Prompts

### System Design
```
Design a system architecture for:

Purpose: Real-time Bloomberg data visualization platform
Users: [NUMBER] concurrent
Data: [LIST DATA TYPES]
Update frequency: [MILLISECONDS]
SLA: [UPTIME %]

Provide:
1. Component diagram
2. Data flow architecture
3. Technology choices with rationale
4. Scaling strategy
5. Disaster recovery plan
6. Cost estimation
7. Implementation phases
```

### Microservice Design
```
Convert this monolithic Bloomberg integration into microservices:
[DESCRIBE CURRENT SYSTEM]

Requirements:
- Service boundaries
- API contracts
- Message queue selection
- Database per service
- Service discovery
- Circuit breakers
- Monitoring strategy

Output service definitions and Docker compose file.
```

## 📈 Trading Strategy Prompts

### Volatility Trading Strategy
```
Given this volatility surface data:
[PASTE BLOOMBERG DATA]

Design a volatility trading strategy:
1. Entry signals with specific thresholds
2. Position sizing formula
3. Risk management rules
4. Exit conditions
5. Backtest pseudocode
6. Expected return/risk metrics
```

### Options Pricing Model
```
Implement Black-Scholes pricing for FX options using:

Market data:
- Spot: [VALUE]
- Volatility surface: [DATA]
- Risk-free rates: [DATA]

Create:
1. Pricing function
2. Greeks calculation
3. Volatility interpolation
4. Model validation
5. Visualization code
```

## 🔧 DevOps Prompts

### Docker Configuration
```
Create Docker setup for Bloomberg integration app:

Components:
- React frontend
- Python API backend  
- Redis cache
- PostgreSQL database

Include:
1. Multi-stage Dockerfiles
2. Docker-compose.yml
3. Environment configuration
4. Health checks
5. Volume management
6. Network security
7. Production optimizations
```

### CI/CD Pipeline
```
Design GitHub Actions workflow for:

Project: Bloomberg Terminal Integration
Stages: Build -> Test -> Security Scan -> Deploy
Environments: Dev, Staging, Prod

Include:
1. Automated tests
2. Code quality checks
3. Security scanning
4. Azure deployment
5. Rollback strategy
6. Notifications
```

## 📝 Documentation Prompts

### API Documentation
```
Generate OpenAPI 3.0 documentation for:
[PASTE API CODE OR DESCRIPTION]

Include:
1. All endpoints with methods
2. Request/response schemas
3. Authentication details
4. Error responses
5. Example requests
6. Rate limiting info
7. Webhooks if applicable
```

### README Generator
```
Create a comprehensive README.md for:

Project: [NAME]
Purpose: [DESCRIPTION]
Tech Stack: [LIST]

Sections:
1. Overview with architecture diagram
2. Prerequisites
3. Installation (multiple OS)
4. Configuration
5. Usage examples
6. API reference
7. Troubleshooting
8. Contributing guidelines
9. License
```

## 🎯 Best Practices for Gemini CLI

### Prompt Structure
1. **Be Specific**: Include exact requirements, not general descriptions
2. **Provide Context**: Explain the business purpose and constraints
3. **Give Examples**: Show input/output formats when possible
4. **Set Boundaries**: Specify what NOT to include
5. **Request Format**: Ask for specific output format (JSON, Markdown, etc.)

### Effective Usage
```powershell
# For long prompts, use files
gemini "$(Get-Content prompt.txt -Raw)"

# For code generation, redirect output
gemini "Generate React component" > Component.tsx

# For analysis, use structured data
$data | ConvertTo-Json | gemini "Analyze this data"

# Chain commands for complex tasks
gemini "Generate types" | gemini "Now create component using these types"
```

### Getting Better Results
1. **Temperature Settings**:
   - 0.1-0.3: Code generation, precise tasks
   - 0.4-0.6: Analysis, balanced creativity
   - 0.7-0.9: Creative writing, brainstorming

2. **Model Selection**:
   - `gemini-pro`: General tasks, code, analysis
   - `gemini-pro-vision`: Image analysis, screenshots
   - `gemini-ultra`: Complex reasoning (when available)

3. **Iterative Refinement**:
   ```powershell
   # First pass
   $v1 = gemini "Generate basic component"
   
   # Refine
   $v2 = gemini "Add error handling to: $v1"
   
   # Polish
   $v3 = gemini "Add tests for: $v2"
   ```

Remember: The more specific and structured your prompt, the better Gemini's response will be!

—SOFTWARE_RESEARCH_ANALYST