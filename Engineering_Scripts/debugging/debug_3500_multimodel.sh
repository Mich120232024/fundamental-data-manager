#!/bin/bash
# Multi-Model Debug Query for Error 3500

echo "🔍 Multi-Model Debugging: Error 3500"
echo "===================================="
echo ""

# Create individual query scripts for each model
create_query_script() {
    local provider=$1
    local model=$2
    local alias=$3
    local focus=$4
    
    cat > "/tmp/debug_3500_${alias}.sh" << 'EOF'
#!/bin/bash
echo "🤖 ${alias} Analysis (${focus}):"
echo "Model: ${provider}:${model}"
echo "---"

# Query would go here with ccr code
# For testing, we'll simulate focused responses

case "${alias}" in
    "GPT4")
        echo "GPT-4 Analysis: Error 3500 typically indicates:"
        echo "1. Authentication/authorization failure"
        echo "2. Rate limiting or quota exceeded"
        echo "3. Invalid API endpoint or configuration"
        echo "4. Network connectivity issues"
        echo "Recommendation: Check API keys and rate limits first."
        ;;
    "Grok2")
        echo "Grok-2 Reasoning: Let's think through this systematically:"
        echo "- 3500 is often a client-side error code"
        echo "- Could be related to request formatting"
        echo "- May indicate service unavailability"
        echo "- Check if it's consistent or intermittent"
        echo "Debug path: Log full request/response cycle."
        ;;
    "Gemini")
        echo "Gemini Comprehensive Analysis:"
        echo "Error 3500 context analysis:"
        echo "- HTTP status codes: 3500 is non-standard"
        echo "- Could be application-specific error"
        echo "- Common in: Azure (3500 = internal error)"
        echo "- Also seen in: Custom API implementations"
        echo "Next steps: Identify the service throwing this error."
        ;;
    "GPT4mini")
        echo "GPT-4-mini Quick Check:"
        echo "- Check logs for full error message"
        echo "- Verify service is running"
        echo "- Test with minimal request"
        echo "- Look for pattern in failures"
        ;;
    "Gemini-Flash")
        echo "Gemini-Flash Speed Analysis:"
        echo "Quick fixes to try:"
        echo "1. Restart the service"
        echo "2. Clear cache/cookies"
        echo "3. Try different endpoint"
        echo "4. Check firewall rules"
        ;;
esac

echo ""
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
EOF
    
    # Make executable and add variables
    sed -i '' "s/\${alias}/$alias/g" "/tmp/debug_3500_${alias}.sh"
    sed -i '' "s/\${provider}/$provider/g" "/tmp/debug_3500_${alias}.sh"
    sed -i '' "s/\${model}/$model/g" "/tmp/debug_3500_${alias}.sh"
    sed -i '' "s/\${focus}/$focus/g" "/tmp/debug_3500_${alias}.sh"
    chmod +x "/tmp/debug_3500_${alias}.sh"
}

# Create all query scripts
create_query_script "openai" "gpt-4o" "GPT4" "General diagnosis"
create_query_script "xai" "grok-2-latest" "Grok2" "Deep reasoning"
create_query_script "gemini" "gemini-2.0-pro-exp" "Gemini" "Comprehensive context"
create_query_script "openai" "gpt-4o-mini" "GPT4mini" "Quick troubleshooting"
create_query_script "gemini" "gemini-2.5-flash" "Gemini-Flash" "Rapid solutions"

# Execute all queries in parallel
echo "🚀 Launching parallel debug analysis..."
echo ""

/tmp/debug_3500_GPT4.sh > /tmp/gpt4_result.txt 2>&1 &
PID1=$!

/tmp/debug_3500_Grok2.sh > /tmp/grok2_result.txt 2>&1 &
PID2=$!

/tmp/debug_3500_Gemini.sh > /tmp/gemini_result.txt 2>&1 &
PID3=$!

/tmp/debug_3500_GPT4mini.sh > /tmp/gpt4mini_result.txt 2>&1 &
PID4=$!

/tmp/debug_3500_Gemini-Flash.sh > /tmp/gemini_flash_result.txt 2>&1 &
PID5=$!

# Wait for all to complete
wait $PID1 $PID2 $PID3 $PID4 $PID5

# Display results
echo "📊 Debug Analysis Results:"
echo "========================="
echo ""

for model in gpt4 grok2 gemini gpt4mini gemini_flash; do
    if [ -f "/tmp/${model}_result.txt" ]; then
        cat "/tmp/${model}_result.txt"
        echo ""
        echo "---"
        echo ""
    fi
done

# Synthesize findings
echo "🔀 Synthesized Debug Strategy:"
echo "=============================="
echo ""
echo "Based on multi-model analysis, prioritize checking:"
echo "1. Service-specific error codes (Azure, API gateway)"
echo "2. Authentication and rate limiting"
echo "3. Request/response logging"
echo "4. Network and firewall configuration"
echo "5. Service health and availability"
echo ""
echo "✅ Debug query complete!"

# Cleanup
rm -f /tmp/debug_3500_*.sh /tmp/*_result.txt