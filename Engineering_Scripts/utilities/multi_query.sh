#!/bin/bash
# Multi-Model Query Script
# Usage: ./multi_query.sh "Your question here"

QUESTION="$1"

if [ -z "$QUESTION" ]; then
    echo "Usage: $0 'Your question here'"
    exit 1
fi

echo "🔄 Starting Multi-Model Query..."
echo "Question: $QUESTION"
echo "=" | tr '=' '=%.0s' {1..60}

# Function to query a model
query_model() {
    local provider=$1
    local model=$2
    local alias=$3
    local output_file="/tmp/${alias}_response.md"
    
    echo "🤖 Querying $alias..."
    
    # Create a query script
    cat > "/tmp/query_${alias}.sh" << EOF
#!/bin/bash
# Query $alias
ccr code << 'QUERY'
/model $provider,$model
$QUESTION

Please provide a concise answer (2-3 sentences).
QUERY
EOF
    
    chmod +x "/tmp/query_${alias}.sh"
    
    # Run in background
    "/tmp/query_${alias}.sh" > "$output_file" 2>&1 &
}

# Launch queries in parallel
query_model "openai" "gpt-4o" "GPT4" &
PID1=$!

query_model "xai" "grok-2-latest" "Grok2" &
PID2=$!

query_model "gemini" "gemini-2.0-pro-exp" "Gemini2" &
PID3=$!

query_model "openai" "gpt-4o-mini" "GPT4mini" &
PID4=$!

# Wait for all to complete
echo ""
echo "⏳ Waiting for responses..."
wait $PID1 $PID2 $PID3 $PID4

echo ""
echo "📊 Results Summary:"
echo "=" | tr '=' '=%.0s' {1..60}

# Display results
for model in GPT4 Grok2 Gemini2 GPT4mini; do
    echo ""
    echo "### $model Response:"
    if [ -f "/tmp/${model}_response.md" ]; then
        head -n 10 "/tmp/${model}_response.md"
    else
        echo "(No response received)"
    fi
    echo "---"
done

echo ""
echo "✅ Multi-model query complete!"
