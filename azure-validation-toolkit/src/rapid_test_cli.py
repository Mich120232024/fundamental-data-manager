#!/usr/bin/env python3
"""
Rapid CLI Testing - Fast validation of all 88 CLI tools
"""
import json
import subprocess
from datetime import datetime

# Load tools
with open("/Users/mikaeleage/Research & Analytics Services/azure_tools_comprehensive.json", 'r') as f:
    data = json.load(f)

cli_tools = [tool for tool in data['tools'] if tool['tool_type'] == 'cli']
print(f"🚀 RAPID CLI TESTING - {len(cli_tools)} tools")
print(f"Start: {datetime.now().strftime('%H:%M:%S')}")

results = []
for i, tool in enumerate(cli_tools, 1):
    cmd = tool['command']
    try:
        # Quick help test only
        result = subprocess.run(f"{cmd} --help".split(), capture_output=True, timeout=10)
        status = "tested" if result.returncode == 0 else "failed"
        print(f"[{i:2d}/88] {tool['id']:30} {status.upper()}")
    except:
        status = "failed"
        print(f"[{i:2d}/88] {tool['id']:30} FAILED")
    
    results.append({
        "tool_id": tool['id'],
        "command": cmd,
        "status": status,
        "timestamp": datetime.now().isoformat()
    })

# Summary
tested = len([r for r in results if r['status'] == 'tested'])
failed = len([r for r in results if r['status'] == 'failed'])

print(f"\n🎯 CLI RESULTS: {tested} tested, {failed} failed")
print(f"Success Rate: {tested/len(results)*100:.1f}%")
print(f"End: {datetime.now().strftime('%H:%M:%S')}")

# Save evidence
with open("logs/cli_rapid_results.json", 'w') as f:
    json.dump(results, f, indent=2)

print("✅ CLI testing complete!")