#!/usr/bin/env python3
"""
Claude Code Server - FastAPI wrapper for Claude Code CLI
"""
import asyncio
import json
import os
import subprocess
import tempfile
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel


class ClaudeRequest(BaseModel):
    task: str
    context: Optional[Dict] = None
    model: Optional[str] = "sonnet"
    timeout: Optional[int] = 300


class ClaudeResponse(BaseModel):
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None
    execution_time: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    print("Claude Code Server starting...")
    # Verify Claude CLI is available
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True, text=True)
        print(f"Claude Code CLI version: {result.stdout.strip()}")
    except Exception as e:
        print(f"Error: Claude CLI not found: {e}")
    yield
    print("Claude Code Server shutting down...")


app = FastAPI(
    title="Claude Code Server",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Check if Claude CLI is available
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "ready", "claude_available": True}
    except:
        pass
    return {"status": "not_ready", "claude_available": False}


@app.post("/execute", response_model=ClaudeResponse)
async def execute_task(request: ClaudeRequest):
    """Execute a Claude Code task"""
    start_time = datetime.utcnow()
    
    try:
        # Build command
        cmd = [
            "claude",
            "--print",
            "--output-format", "json",
            "--model", request.model,
            "--dangerously-skip-permissions"  # Since we're in a container
        ]
        
        # Add allowed tools
        cmd.extend(["--allowedTools", "filesystem,azure,github,memory"])
        
        # Create prompt with context if provided
        prompt = request.task
        if request.context:
            prompt = f"Context: {json.dumps(request.context)}\n\nTask: {request.task}"
        
        # Execute Claude Code
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Send prompt and get response
        stdout, stderr = await asyncio.wait_for(
            process.communicate(prompt.encode()),
            timeout=request.timeout
        )
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        if process.returncode != 0:
            return ClaudeResponse(
                success=False,
                error=f"Claude Code error: {stderr.decode()}",
                execution_time=execution_time
            )
        
        try:
            result = json.loads(stdout.decode())
            return ClaudeResponse(
                success=True,
                result=result,
                execution_time=execution_time
            )
        except json.JSONDecodeError:
            # Return raw text if not JSON
            return ClaudeResponse(
                success=True,
                result={"output": stdout.decode()},
                execution_time=execution_time
            )
            
    except asyncio.TimeoutError:
        return ClaudeResponse(
            success=False,
            error=f"Task timed out after {request.timeout} seconds",
            execution_time=request.timeout
        )
    except Exception as e:
        return ClaudeResponse(
            success=False,
            error=str(e),
            execution_time=(datetime.utcnow() - start_time).total_seconds()
        )


@app.post("/database/analyze")
async def analyze_database(request: Request):
    """Analyze Cosmos DB data"""
    body = await request.json()
    query = body.get("query", "")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query required")
    
    task = f"Analyze the Cosmos DB data with this query: {query}"
    
    claude_request = ClaudeRequest(task=task)
    return await execute_task(claude_request)


@app.post("/architecture/design")
async def design_architecture(request: Request):
    """Design system architecture"""
    body = await request.json()
    requirements = body.get("requirements", "")
    
    if not requirements:
        raise HTTPException(status_code=400, detail="Requirements needed")
    
    task = f"Design a system architecture for: {requirements}"
    
    claude_request = ClaudeRequest(task=task)
    return await execute_task(claude_request)


@app.post("/code/analyze")
async def analyze_code(request: Request):
    """Analyze code repository"""
    body = await request.json()
    repo_path = body.get("repo_path", "")
    analysis_type = body.get("analysis_type", "general")
    
    if not repo_path:
        raise HTTPException(status_code=400, detail="Repository path required")
    
    task = f"Analyze the code at {repo_path} for {analysis_type}"
    
    claude_request = ClaudeRequest(task=task)
    return await execute_task(claude_request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)