# Bloomberg-Gemini Integration Helper Script
# This script provides useful functions for working with Bloomberg data using Gemini CLI

# Set up environment
$BLOOMBERG_API = "http://20.172.249.92:8080"
$GEMINI_API_KEY = "AIzaSyAnnu1klwX6l-WTzMb1wpdCGNjeln0ERD4"

# Ensure API key is set
if (-not $env:GEMINI_API_KEY) {
    [System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $GEMINI_API_KEY, "User")
    $env:GEMINI_API_KEY = $GEMINI_API_KEY
}

# Function to fetch Bloomberg data
function Get-BloombergData {
    param(
        [string[]]$Securities,
        [string[]]$Fields = @("PX_LAST")
    )
    
    $body = @{
        securities = $Securities
        fields = $Fields
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BLOOMBERG_API/api/market-data" -Method POST -Body $body -ContentType "application/json"
        return $response
    }
    catch {
        Write-Error "Failed to fetch Bloomberg data: $_"
        return $null
    }
}

# Function to analyze volatility surface with Gemini
function Analyze-VolatilitySurface {
    param(
        [string]$Currency = "EURUSD"
    )
    
    Write-Host "Fetching volatility data for $Currency..." -ForegroundColor Yellow
    
    # Define securities
    $securities = @(
        "${Currency}V1M Curncy",
        "${Currency}V2M Curncy",
        "${Currency}V3M Curncy",
        "${Currency}V6M Curncy",
        "${Currency}V1Y Curncy"
    )
    
    if ($Currency -eq "EURUSD") {
        $securities += @(
            "EUR25R1M Curncy",
            "EUR25R3M Curncy",
            "EUR25R6M Curncy",
            "EUR25B1M Curncy",
            "EUR25B3M Curncy",
            "EUR25B6M Curncy"
        )
    }
    
    # Fetch data
    $data = Get-BloombergData -Securities $securities
    
    if ($data) {
        $jsonData = $data | ConvertTo-Json -Depth 10
        
        $prompt = @"
Analyze this Bloomberg FX volatility surface data:
$jsonData

Please provide:
1. Current market sentiment based on risk reversals
2. Volatility smile characteristics from butterflies
3. Term structure analysis
4. Any unusual patterns or anomalies
5. Trading recommendations
"@
        
        Write-Host "Analyzing with Gemini..." -ForegroundColor Green
        $analysis = gemini $prompt
        
        # Save analysis
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $filename = "vol_analysis_${Currency}_${timestamp}.md"
        $analysis | Out-File -FilePath $filename -Encoding UTF8
        
        Write-Host "Analysis saved to: $filename" -ForegroundColor Cyan
        return $analysis
    }
}

# Function to generate React code for Bloomberg data
function Generate-BloombergComponent {
    param(
        [string]$ComponentName,
        [string]$DataType = "volatility"
    )
    
    $prompt = @"
Generate a complete React TypeScript component named $ComponentName that:

1. Fetches $DataType data from Bloomberg API endpoint '/api/market-data'
2. Uses these TypeScript interfaces:
   - MarketData { security: string, fields: Record<string, number> }
   - VolatilitySurface { tenor: string, atm: number, rr25: number, bf25: number }
3. Implements:
   - Real-time updates every 30 seconds
   - Error handling with retry logic
   - Loading and error states
   - Tailwind CSS styling
   - Responsive design
4. For volatility data, calculate 25-delta calls/puts using:
   - Call vol = ATM + BF + RR/2
   - Put vol = ATM + BF - RR/2

Include all imports and make it production-ready.
"@
    
    Write-Host "Generating $ComponentName component..." -ForegroundColor Yellow
    $code = gemini $prompt
    
    $filename = "$ComponentName.tsx"
    $code | Out-File -FilePath $filename -Encoding UTF8
    
    Write-Host "Component saved to: $filename" -ForegroundColor Green
    return $filename
}

# Function to debug Bloomberg API issues
function Debug-BloombergConnection {
    Write-Host "Testing Bloomberg API connection..." -ForegroundColor Yellow
    
    # Test health endpoint
    try {
        $health = Invoke-RestMethod -Uri "$BLOOMBERG_API/health"
        Write-Host "✓ API is running" -ForegroundColor Green
        Write-Host "  Bloomberg connected: $($health.bloomberg_connected)" -ForegroundColor Cyan
        Write-Host "  Server version: $($health.version)" -ForegroundColor Cyan
    }
    catch {
        Write-Host "✗ API is not responding" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        
        $debugPrompt = @"
The Bloomberg API at $BLOOMBERG_API is not responding with error:
$_

Common causes and solutions:
1. API server not running
2. Firewall blocking connection
3. Bloomberg Terminal not logged in

Provide step-by-step troubleshooting instructions.
"@
        
        $solution = gemini $debugPrompt
        Write-Host "`nTroubleshooting suggestions:" -ForegroundColor Yellow
        Write-Host $solution
        return
    }
    
    # Test data endpoint
    Write-Host "`nTesting market data endpoint..." -ForegroundColor Yellow
    $testData = Get-BloombergData -Securities @("EURUSD Curncy") -Fields @("PX_LAST")
    
    if ($testData) {
        Write-Host "✓ Market data endpoint working" -ForegroundColor Green
        Write-Host "  Sample data: $($testData | ConvertTo-Json -Compress)" -ForegroundColor Cyan
    }
    else {
        Write-Host "✗ Market data endpoint failed" -ForegroundColor Red
    }
}

# Function to compare Terminal vs API values
function Compare-TerminalVsAPI {
    param(
        [hashtable]$TerminalValues,
        [string[]]$Securities
    )
    
    Write-Host "Fetching API values..." -ForegroundColor Yellow
    $apiData = Get-BloombergData -Securities $Securities
    
    $comparison = @()
    foreach ($sec in $Securities) {
        $terminalVal = $TerminalValues[$sec]
        $apiVal = $apiData.data.$sec.PX_LAST
        $diff = [math]::Abs($terminalVal - $apiVal)
        
        $comparison += @{
            Security = $sec
            Terminal = $terminalVal
            API = $apiVal
            Difference = $diff
            PercentDiff = [math]::Round(($diff / $terminalVal) * 100, 2)
        }
    }
    
    $comparisonJson = $comparison | ConvertTo-Json -Depth 10
    
    $prompt = @"
Analyze these discrepancies between Bloomberg Terminal and API values:
$comparisonJson

Explain:
1. Why these differences might occur
2. Which values to trust
3. How to fix the discrepancies
4. Impact on trading decisions
"@
    
    Write-Host "Analyzing discrepancies with Gemini..." -ForegroundColor Green
    $analysis = gemini $prompt
    
    Write-Host "`nDiscrepancy Analysis:" -ForegroundColor Cyan
    Write-Host $analysis
    
    return $comparison
}

# Function to generate Python analysis script
function Generate-PythonAnalysis {
    param(
        [string]$AnalysisType = "volatility_surface"
    )
    
    $prompt = @"
Generate a complete Python script for $AnalysisType analysis that:

1. Uses the Bloomberg API at $BLOOMBERG_API
2. Implements a Bloomberg client class with:
   - Connection handling
   - Data fetching methods
   - Error handling and retries
3. For volatility surface:
   - Fetch ATM vols, risk reversals, butterflies
   - Calculate full volatility smile
   - Generate 3D surface plot using matplotlib
   - Export to JSON and CSV
4. Include:
   - Type hints
   - Logging
   - Command line arguments
   - Requirements.txt content

Make it production-ready with proper error handling.
"@
    
    Write-Host "Generating Python $AnalysisType script..." -ForegroundColor Yellow
    $code = gemini $prompt
    
    $filename = "bloomberg_$AnalysisType.py"
    $code | Out-File -FilePath $filename -Encoding UTF8
    
    Write-Host "Python script saved to: $filename" -ForegroundColor Green
    return $filename
}

# Interactive menu
function Show-Menu {
    Clear-Host
    Write-Host "=== Bloomberg-Gemini Integration Tool ===" -ForegroundColor Cyan
    Write-Host "1. Test Bloomberg connection"
    Write-Host "2. Analyze volatility surface"
    Write-Host "3. Generate React component"
    Write-Host "4. Generate Python analysis script"
    Write-Host "5. Compare Terminal vs API values"
    Write-Host "6. Debug connection issues"
    Write-Host "Q. Quit"
    Write-Host ""
}

# Main loop
if ($args.Count -eq 0) {
    do {
        Show-Menu
        $choice = Read-Host "Select option"
        
        switch ($choice) {
            "1" { Debug-BloombergConnection; Read-Host "Press Enter to continue" }
            "2" { 
                $currency = Read-Host "Enter currency pair (default: EURUSD)"
                if (-not $currency) { $currency = "EURUSD" }
                Analyze-VolatilitySurface -Currency $currency
                Read-Host "Press Enter to continue"
            }
            "3" {
                $name = Read-Host "Enter component name"
                Generate-BloombergComponent -ComponentName $name
                Read-Host "Press Enter to continue"
            }
            "4" {
                Generate-PythonAnalysis
                Read-Host "Press Enter to continue"
            }
            "5" {
                Write-Host "Enter Terminal values (e.g., EURUSDV1M=8.760):"
                $values = @{}
                while ($true) {
                    $input = Read-Host "Security=Value (or press Enter to finish)"
                    if (-not $input) { break }
                    $parts = $input.Split('=')
                    $values[$parts[0]] = [double]$parts[1]
                }
                Compare-TerminalVsAPI -TerminalValues $values -Securities $values.Keys
                Read-Host "Press Enter to continue"
            }
            "6" {
                Debug-BloombergConnection
                Read-Host "Press Enter to continue"
            }
        }
    } while ($choice -ne "Q")
}

# Export functions for use in other scripts
Export-ModuleMember -Function Get-BloombergData, Analyze-VolatilitySurface, Generate-BloombergComponent, Debug-BloombergConnection, Compare-TerminalVsAPI, Generate-PythonAnalysis

Write-Host "Bloomberg-Gemini Integration loaded. Available functions:" -ForegroundColor Green
Write-Host "  Get-BloombergData" -ForegroundColor Cyan
Write-Host "  Analyze-VolatilitySurface" -ForegroundColor Cyan
Write-Host "  Generate-BloombergComponent" -ForegroundColor Cyan
Write-Host "  Debug-BloombergConnection" -ForegroundColor Cyan
Write-Host "  Compare-TerminalVsAPI" -ForegroundColor Cyan
Write-Host "  Generate-PythonAnalysis" -ForegroundColor Cyan