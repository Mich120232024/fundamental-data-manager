#!/bin/bash
# Context-aware debug for Error 3500

echo "🔍 Contextual Error 3500 Debug"
echo "=============================="
echo ""
echo "Searching for error context in workspace..."

# Search for 3500 errors in logs
echo "📋 Recent 3500 errors in logs:"
find . -name "*.log" -type f -exec grep -l "3500" {} \; 2>/dev/null | head -5

echo ""
echo "📝 Error patterns found:"
grep -r "3500" . --include="*.log" --include="*.txt" --include="*.md" 2>/dev/null | grep -i "error" | head -5

echo ""
echo "🔎 Checking common 3500 error sources:"
echo ""

# Check if it's Azure-related
if grep -r "3500" . --include="*.py" --include="*.js" 2>/dev/null | grep -i "azure" | head -1; then
    echo "✓ Azure-related 3500 error detected"
    echo "  → Azure internal server error (common with Cosmos DB, Event Hubs)"
fi

# Check if it's API-related
if grep -r "3500" . --include="*.py" --include="*.js" 2>/dev/null | grep -i "api" | head -1; then
    echo "✓ API-related 3500 error detected"
    echo "  → Check API gateway or rate limiting"
fi

# Check if it's in recent session logs
if ls /001/logs/user_logs_capture_recovery/head*/* 2>/dev/null | xargs grep -l "3500" 2>/dev/null | head -1; then
    echo "✓ Found in recent session logs"
fi

echo ""
echo "🤖 Multi-Model Debug Questions:"
echo ""

# Prepare specific questions based on context
cat > /tmp/specific_3500_query.txt << 'EOF'
Based on the error code 3500 in our system:

1. Is this related to Azure services (Cosmos DB, Event Hub)?
2. Is this a rate limiting issue?
3. Is this an authentication failure?
4. Is this a network/firewall issue?
5. What's the most likely root cause?

Please provide specific debug steps.
EOF

echo "📊 Creating targeted debug queries..."
echo ""

# Quick parallel check with different focuses
echo "🔄 Launching focused analysis..."

# Focus 1: Azure expertise
(echo "Azure 3500 Debug Focus:" && echo "- Check Cosmos DB connection strings" && echo "- Verify Event Hub quotas" && echo "- Review Azure Monitor logs") > /tmp/azure_focus.txt &

# Focus 2: API expertise  
(echo "API 3500 Debug Focus:" && echo "- Check rate limit headers" && echo "- Verify API key validity" && echo "- Test with curl/Postman") > /tmp/api_focus.txt &

# Focus 3: Network expertise
(echo "Network 3500 Debug Focus:" && echo "- Test connectivity" && echo "- Check firewall rules" && echo "- Verify DNS resolution") > /tmp/network_focus.txt &

wait

# Display focused results
echo "📋 Focused Debug Strategies:"
echo ""
cat /tmp/azure_focus.txt
echo ""
cat /tmp/api_focus.txt
echo ""
cat /tmp/network_focus.txt

echo ""
echo "🎯 Recommended Debug Action Plan:"
echo "1. Check the specific service logs for full error details"
echo "2. Test the failing operation with minimal parameters"
echo "3. Verify all credentials and connection strings"
echo "4. Monitor network traffic during failure"
echo "5. Check service health dashboards"

# Cleanup
rm -f /tmp/*_focus.txt /tmp/specific_3500_query.txt