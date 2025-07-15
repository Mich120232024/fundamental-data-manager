#!/usr/bin/env python3
"""
Claude Code Database Specialist - Same Network as Databases
Deploy to AKS gzc-trading namespace for direct database access
"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import asyncio
import os
from typing import AsyncGenerator

app = FastAPI(title="Claude Code Database Specialist")

# HTML Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Claude Code - Database Architecture Specialist</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #2563eb; margin: 0; }
        .header p { color: #6b7280; margin: 5px 0 0 0; }
        .chat-container { display: flex; gap: 20px; height: 70vh; }
        .input-section { flex: 1; display: flex; flex-direction: column; }
        .output-section { flex: 1; display: flex; flex-direction: column; }
        textarea { width: 100%; height: 200px; border: 1px solid #d1d5db; border-radius: 6px; padding: 12px; font-family: monospace; font-size: 14px; resize: vertical; }
        .output { height: 100%; border: 1px solid #d1d5db; border-radius: 6px; padding: 12px; background: #f9fafb; overflow-y: auto; font-family: monospace; font-size: 14px; white-space: pre-wrap; }
        .controls { margin: 10px 0; }
        button { background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
        button:hover { background: #1d4ed8; }
        button:disabled { background: #9ca3af; cursor: not-allowed; }
        .status { padding: 8px 12px; border-radius: 4px; margin: 10px 0; }
        .status.connected { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
        .status.error { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
        .examples { margin-top: 15px; }
        .example { background: #f3f4f6; padding: 8px 12px; border-radius: 4px; margin: 5px 0; cursor: pointer; font-size: 13px; }
        .example:hover { background: #e5e7eb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Claude Code - Database Architecture Specialist</h1>
            <p>Azure-hosted Claude Code for database architecture, building, and retrieval</p>
        </div>
        
        <div class="status connected">
            ✅ Connected to AKS Claude Code Specialist | Same Network as Cosmos DB | Direct Database Access
        </div>

        <div class="chat-container">
            <div class="input-section">
                <h3>💬 Ask the Database Specialist</h3>
                <form id="promptForm">
                    <textarea id="promptInput" placeholder="Example: Design a Cosmos DB schema for financial trading data with optimal partitioning..."></textarea>
                    <div class="controls">
                        <button type="submit" id="submitBtn">Send to Claude Code</button>
                        <button type="button" onclick="clearAll()">Clear</button>
                    </div>
                </form>
                
                <div class="examples">
                    <strong>Quick Examples:</strong>
                    <div class="example" onclick="setPrompt('Design a Cosmos DB schema for financial trading data with optimal partitioning')">🗄️ Design Cosmos DB trading schema</div>
                    <div class="example" onclick="setPrompt('Create a data retrieval strategy for FRED economic data with caching')">📊 FRED data retrieval strategy</div>
                    <div class="example" onclick="setPrompt('Build SQL queries for time-series analysis of market data')">📈 Time-series SQL queries</div>
                    <div class="example" onclick="setPrompt('Architect a data pipeline from API to analytics dashboard')">⚡ Data pipeline architecture</div>
                </div>
            </div>
            
            <div class="output-section">
                <h3>🤖 Claude Code Response</h3>
                <div id="output" class="output">Waiting for your database architecture question...</div>
            </div>
        </div>
    </div>

    <script>
        let isProcessing = false;

        document.getElementById('promptForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            if (isProcessing) return;
            
            const prompt = document.getElementById('promptInput').value.trim();
            if (!prompt) return;
            
            isProcessing = true;
            const submitBtn = document.getElementById('submitBtn');
            const output = document.getElementById('output');
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            output.textContent = 'Claude Code is thinking about your database architecture question...\\n';
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `prompt=${encodeURIComponent(prompt)}`
                });
                
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                output.textContent = '';
                
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    output.textContent += chunk;
                    output.scrollTop = output.scrollHeight;
                }
            } catch (error) {
                output.textContent = `Error: ${error.message}`;
            } finally {
                isProcessing = false;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send to Claude Code';
            }
        });

        function setPrompt(text) {
            document.getElementById('promptInput').value = text;
        }

        function clearAll() {
            document.getElementById('promptInput').value = '';
            document.getElementById('output').textContent = 'Waiting for your database architecture question...';
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def web_interface():
    """Web interface for Claude Code Database Specialist."""
    return HTML_TEMPLATE

@app.post("/ask")
async def ask_claude_code(prompt: str = Form(...)):
    """Stream Claude Code response for database questions."""
    
    # Add database-specific context to prompt
    enhanced_prompt = f"""
You are a database architecture specialist. Focus on:
- Database design and optimization
- Cosmos DB, SQL, and NoSQL solutions  
- Data retrieval and query optimization
- ETL pipelines and data architecture
- Performance tuning and scaling

User Question: {prompt}

Provide practical, actionable database architecture guidance.
"""
    
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            # Run Claude Code with the enhanced prompt
            process = await asyncio.create_subprocess_exec(
                "claude", enhanced_prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/workspace"
            )
            
            # Stream output
            while True:
                data = await process.stdout.read(1024)
                if not data:
                    break
                yield data.decode('utf-8', errors='ignore')
            
            await process.wait()
            
        except Exception as e:
            yield f"Error: {str(e)}\n"
            yield "\nFallback: Using local database tools...\n"
            
            # Fallback to local tools if Claude Code not available
            fallback_response = f"""
Database Architecture Analysis for: {prompt}

🏗️ Recommended Approach:
1. Schema Design: Consider partition keys for optimal distribution
2. Query Patterns: Index for most common access patterns  
3. Scaling Strategy: Plan for read/write throughput requirements
4. Data Modeling: Denormalize for read performance in NoSQL

🔧 Implementation Steps:
- Define entity relationships and access patterns
- Choose appropriate database technology (SQL vs NoSQL)
- Design partition strategy for horizontal scaling
- Implement caching layer for frequently accessed data

💡 Best Practices:
- Use proper indexing strategies
- Implement connection pooling
- Monitor query performance
- Plan for backup and disaster recovery

For detailed implementation, please specify your exact requirements.
"""
            yield fallback_response
    
    return StreamingResponse(generate_response(), media_type="text/plain")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Claude Code Database Specialist",
        "capabilities": ["database_design", "cosmos_db", "sql_optimization", "data_architecture"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)