# Gemini CLI Advanced Usage Guide

Since Claude cannot be installed on Windows Server, this guide will help you use Gemini CLI effectively for your Bloomberg Terminal integration and development tasks.

## Table of Contents
1. [Gemini CLI Commands](#gemini-cli-commands)
2. [Bloomberg Data Analysis](#bloomberg-data-analysis)
3. [Code Generation](#code-generation)
4. [Debugging Assistance](#debugging-assistance)
5. [Integration Scripts](#integration-scripts)
6. [Prompt Engineering](#prompt-engineering)

## Gemini CLI Commands

### Basic Usage
```powershell
# Simple query
gemini "What is the current EURUSD volatility?"

# Multi-line query (use triple quotes)
gemini """
Analyze this Bloomberg data:
EURUSDV1M: 8.760%
EUR25R1M: -0.548
EUR25B1M: 0.319
"""

# File analysis
gemini "Analyze this file: $(Get-Content 'data.json' -Raw)"
```

### Advanced Flags
```powershell
# Specify model
gemini --model gemini-pro "Your query"
gemini --model gemini-pro-vision "Analyze this image" --image screenshot.png

# Temperature control (creativity)
gemini --temperature 0.1 "Generate precise code"  # More deterministic
gemini --temperature 0.9 "Creative writing task"  # More creative

# Token limits
gemini --max-tokens 2000 "Long response needed"
```

## Bloomberg Data Analysis

### Volatility Surface Analysis
```powershell
# Analyze volatility data
$prompt = @"
I have Bloomberg Terminal volatility data for EURUSD:

ATM Vols:
- EURUSDV1M: 8.760%
- EURUSDV2M: 7.890%
- EURUSDV3M: 7.450%

Risk Reversals (25D):
- EUR25R1M: -0.548
- EUR25R2M: -0.623
- EUR25R3M: -0.701

Butterflies (25D):
- EUR25B1M: 0.319
- EUR25B2M: 0.342
- EUR25B3M: 0.365

Please:
1. Calculate the 25-delta call and put volatilities
2. Identify any market sentiment indicators
3. Suggest trading strategies based on this surface
"@

gemini $prompt
```

### API Data Comparison
```powershell
# Compare Terminal vs API values
$comparison = @"
Bloomberg Terminal shows:
- EURUSDV1M: 8.760%

API returns:
- EURUSDV1M: 7.638%

Difference: 1.122%

What could cause this discrepancy and how to fix it?
"@

gemini $comparison
```

## Code Generation

### React Component Generation
```powershell
$reactPrompt = @"
Generate a React component for displaying Bloomberg FX volatility data with these requirements:
1. TypeScript with proper types
2. Real-time data updates via WebSocket
3. Display ATM vols, risk reversals, and butterflies
4. Use Tailwind CSS for styling
5. Include error handling and loading states
"@

gemini $reactPrompt > VolatilityDisplay.tsx
```

### Python Bloomberg Integration
```powershell
$pythonPrompt = @"
Create a Python class for Bloomberg Terminal integration that:
1. Connects to Bloomberg API at http://20.172.249.92:8080
2. Fetches FX volatility surface data
3. Calculates implied volatilities for different strikes
4. Exports data to JSON and CSV formats
5. Includes proper error handling and logging
"@

gemini $pythonPrompt > bloomberg_integration.py
```

## Debugging Assistance

### Error Analysis
```powershell
# Analyze error messages
$error = Get-Content "error.log" -Tail 50
$debugPrompt = @"
I'm getting this error in my Bloomberg integration:
$error

The code is trying to fetch volatility data from the Bloomberg Terminal.
Please identify the issue and provide a fix.
"@

gemini $debugPrompt
```

### Performance Optimization
```powershell
$perfPrompt = @"
My React app is slow when updating volatility surfaces. Here's the component:
$(Get-Content 'VolatilitySurface.tsx' -Raw)

How can I optimize this for better performance?
"@

gemini $perfPrompt
```

## Integration Scripts

### Create a Gemini Helper Script
Save as `gemini-helper.ps1`:

```powershell
# Gemini Helper Functions

function Analyze-BloombergData {
    param(
        [string]$DataFile
    )
    
    $data = Get-Content $DataFile -Raw
    $prompt = "Analyze this Bloomberg market data and provide insights: $data"
    gemini $prompt
}

function Generate-Code {
    param(
        [string]$Description,
        [string]$Language = "typescript",
        [string]$OutputFile
    )
    
    $prompt = "Generate $Language code for: $Description"
    $code = gemini $prompt
    
    if ($OutputFile) {
        $code | Out-File -FilePath $OutputFile -Encoding UTF8
        Write-Host "Code saved to $OutputFile"
    } else {
        return $code
    }
}

function Debug-Error {
    param(
        [string]$ErrorMessage,
        [string]$CodeFile
    )
    
    $code = if ($CodeFile) { Get-Content $CodeFile -Raw } else { "" }
    $prompt = @"
Debug this error:
Error: $ErrorMessage

Code:
$code

Provide step-by-step debugging instructions.
"@
    
    gemini $prompt
}

function Compare-Data {
    param(
        [string]$Expected,
        [string]$Actual
    )
    
    $prompt = @"
Compare these data sets:
Expected: $Expected
Actual: $Actual

Explain differences and suggest fixes.
"@
    
    gemini $prompt
}

# Usage examples:
# Analyze-BloombergData -DataFile "volatility_data.json"
# Generate-Code -Description "React hook for Bloomberg data" -OutputFile "useBloomberg.ts"
# Debug-Error -ErrorMessage "Cannot read property 'volatility' of undefined" -CodeFile "Surface.tsx"
```

### Automated Analysis Script
Save as `bloomberg-analysis.ps1`:

```powershell
# Automated Bloomberg Data Analysis

# Fetch current data
$response = Invoke-RestMethod -Uri "http://20.172.249.92:8080/api/market-data" -Method POST -Body (@{
    securities = @("EURUSDV1M Curncy", "EUR25R1M Curncy", "EUR25B1M Curncy")
    fields = @("PX_LAST")
} | ConvertTo-Json) -ContentType "application/json"

# Prepare analysis prompt
$analysisPrompt = @"
Analyze this real-time Bloomberg data:
$(ConvertTo-Json $response -Depth 10)

Provide:
1. Market sentiment analysis
2. Volatility smile characteristics
3. Trading recommendations
4. Risk warnings
"@

# Get analysis
$analysis = gemini $analysisPrompt

# Save results
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$analysis | Out-File -FilePath "analysis_$timestamp.md" -Encoding UTF8

Write-Host "Analysis saved to analysis_$timestamp.md"
```

## Prompt Engineering

### Effective Prompts for Technical Tasks

#### 1. Specific Code Generation
```powershell
# Bad prompt:
gemini "Write code for Bloomberg"

# Good prompt:
gemini @"
Write a TypeScript function that:
1. Accepts Bloomberg security IDs (e.g., 'EURUSDV1M Curncy')
2. Fetches data from http://20.172.249.92:8080/api/market-data
3. Returns typed response with error handling
4. Uses axios for HTTP requests
5. Includes JSDoc comments
"@
```

#### 2. Debugging with Context
```powershell
# Provide full context
$debugPrompt = @"
Context: I'm building a React app that displays Bloomberg FX volatility surfaces.
Problem: The 3D surface renders but shows NaN for some volatility values.
Data format: { tenor: '1M', strike: 25, volatility: 8.76 }

The calculation uses:
volatility = ATM + butterfly + (riskReversal * sign(strike))

Debug why some values are NaN.
"@
```

#### 3. Architecture Decisions
```powershell
$archPrompt = @"
I need to architect a system with these requirements:
- Real-time Bloomberg Terminal data ingestion
- React frontend with 3D volatility surfaces
- Historical data storage in Azure
- Sub-second update latency
- Support for 10 concurrent users

Recommend:
1. Technology stack
2. Data flow architecture
3. Caching strategy
4. Error handling approach
"@
```

### Prompt Templates

#### Data Analysis Template
```powershell
$template = @"
Role: You are a quantitative analyst specializing in FX options.
Task: Analyze the following Bloomberg volatility surface data.
Data: [INSERT DATA HERE]
Output format:
1. Summary statistics
2. Market interpretation
3. Anomaly detection
4. Trading signals
Constraints: Focus on actionable insights.
"@
```

#### Code Review Template
```powershell
$reviewTemplate = @"
Review this code for:
1. Performance issues
2. Security vulnerabilities
3. Best practices
4. Potential bugs

Code:
[INSERT CODE HERE]

Provide specific line numbers and fixes.
"@
```

## Batch Processing

### Process Multiple Files
```powershell
# Analyze all Python files
Get-ChildItem -Filter "*.py" | ForEach-Object {
    Write-Host "Analyzing $($_.Name)..."
    $content = Get-Content $_.FullName -Raw
    $analysis = gemini "Review this Python code for Bloomberg integration best practices: $content"
    $analysis | Out-File -FilePath "$($_.BaseName)_review.md" -Encoding UTF8
}
```

### Generate Test Cases
```powershell
# Generate tests for each component
$components = @("VolatilitySurface", "RiskReversal", "Butterfly")

foreach ($component in $components) {
    $testPrompt = @"
Generate comprehensive Jest tests for a React component called $component that:
1. Tests data rendering
2. Tests error states
3. Tests loading states
4. Uses React Testing Library
5. Includes mock Bloomberg data
"@
    
    gemini $testPrompt | Out-File -FilePath "$($component).test.tsx" -Encoding UTF8
}
```

## Troubleshooting Gemini CLI

### Common Issues

1. **API Key Not Working**
   ```powershell
   # Verify environment variable
   echo $env:GEMINI_API_KEY
   
   # Test with curl
   curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$env:GEMINI_API_KEY" -H "Content-Type: application/json" -d '{\"contents\":[{\"parts\":[{\"text\":\"Test\"}]}]}'
   ```

2. **Response Truncated**
   ```powershell
   # Increase token limit
   gemini --max-tokens 4000 "Your long query"
   ```

3. **Rate Limiting**
   ```powershell
   # Add delay between requests
   Start-Sleep -Seconds 2
   ```

## Quick Reference Card

```powershell
# Basic query
gemini "Your question"

# With model selection
gemini --model gemini-pro "Question"

# With temperature
gemini --temperature 0.2 "Precise task"

# From file
gemini "Analyze: $(Get-Content file.txt -Raw)"

# Save output
gemini "Generate code" > output.txt

# Pipe data
Get-Process | ConvertTo-Json | gemini "Analyze this process data"
```

Remember: While Gemini CLI isn't as capable as Claude, with proper prompting and these techniques, you can still get valuable assistance for your Bloomberg integration work.

—SOFTWARE_RESEARCH_ANALYST