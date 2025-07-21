#!/usr/bin/env python3
"""Test the hook concept without Claude"""

import json

# Simulate what the hook should do
def test_hook():
    # 1. Read current agent
    current_agent = "SOFTWARE_AGENT_001"
    
    # 2. Build identity injection
    identity = f"""[AGENT: {current_agent}]
[ROLE: Software Development Agent]

CONCRETE RULES:
1. BEFORE claiming "deployed" → Show actual Azure resource URL
2. BEFORE claiming "working" → Run the code and show output
3. When using Bloomberg API → Check rate limits (100/sec max)

CURRENT PROJECT: test_bloomberg_api
"""
    
    # 3. Simulate prompt modification
    original_prompt = "What project am I working on?"
    modified_prompt = f"{identity}\n\nUser request: {original_prompt}"
    
    print("=== Original Prompt ===")
    print(original_prompt)
    print("\n=== Modified Prompt (what Claude sees) ===")
    print(modified_prompt)

if __name__ == "__main__":
    test_hook()