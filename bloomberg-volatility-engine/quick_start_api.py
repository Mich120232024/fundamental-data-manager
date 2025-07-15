#!/usr/bin/env python3
"""
Quick start Bloomberg API server
"""

import subprocess
import time

def quick_start():
    """Simple API server start"""
    
    print("🚀 Quick Starting Bloomberg API Server")
    print("=" * 60)
    
    # Very simple start command
    start_cmd = r'cd C:\Bloomberg\APIServer && start /B C:\Python311\python.exe bloomberg_api_server.py'
    
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02", 
        "--command-id", "RunPowerShellScript",
        "--scripts", start_cmd,
        "--no-wait"  # Don't wait for completion
    ]
    
    print("Starting API server...")
    subprocess.run(cmd, capture_output=True)
    
    print("Waiting for server to start...")
    time.sleep(10)
    
    # Test connection
    print("\nTesting API connection...")
    test_cmd = ["curl", "-s", "http://20.172.249.92:8080/api/health"]
    result = subprocess.run(test_cmd, capture_output=True, text=True)
    
    if result.stdout and "bloomberg_connected" in result.stdout:
        print("✓ API Server is running!")
        print(result.stdout)
    else:
        print("API Server may still be starting...")
        print("Try testing in a few seconds with:")
        print("curl http://20.172.249.92:8080/api/health")


if __name__ == "__main__":
    quick_start()