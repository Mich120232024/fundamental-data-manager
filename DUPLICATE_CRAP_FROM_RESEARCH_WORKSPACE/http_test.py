#!/usr/bin/env python3
"""
HTTP Test for MCP Server Health Endpoints
"""
import requests
import time
import subprocess
import sys
import os
import signal
from threading import Thread

class MCPServerTester:
    def __init__(self):
        self.server_process = None
        self.base_url = "http://localhost:8082"
        
    def start_server(self):
        """Start the MCP server in background."""
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "simple_mcp_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("🚀 Starting MCP server...")
            time.sleep(3)  # Give server time to start
            return True
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the MCP server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")
    
    def test_health_endpoint(self):
        """Test the /health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Health endpoint working!")
                print(f"   Status: {data.get('status')}")
                print(f"   Service: {data.get('service')}")
                return True
            else:
                print(f"❌ Health endpoint failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return False
    
    def test_ready_endpoint(self):
        """Test the /ready endpoint."""
        try:
            response = requests.get(f"{self.base_url}/ready", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Ready endpoint working!")
                print(f"   Status: {data.get('status')}")
                print(f"   MCP Server: {data.get('mcp_server')}")
                return True
            else:
                print(f"❌ Ready endpoint failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ready endpoint error: {e}")
            return False
    
    def run_tests(self):
        """Run all HTTP tests."""
        print("🧪 MCP Server HTTP Testing")
        print("=" * 40)
        
        if not self.start_server():
            return
        
        try:
            print(f"\n🔗 Testing endpoints at {self.base_url}")
            
            # Test health endpoint
            print("\n1️⃣ Testing /health endpoint:")
            health_ok = self.test_health_endpoint()
            
            # Test ready endpoint
            print("\n2️⃣ Testing /ready endpoint:")
            ready_ok = self.test_ready_endpoint()
            
            # Summary
            print(f"\n📊 Test Summary:")
            print(f"   Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
            print(f"   Ready endpoint: {'✅ PASS' if ready_ok else '❌ FAIL'}")
            
            if health_ok and ready_ok:
                print("\n🎉 All HTTP tests passed! MCP server is working!")
            else:
                print("\n⚠️ Some tests failed. Check server logs.")
                
        finally:
            self.stop_server()

def quick_curl_test():
    """Quick test using curl commands."""
    print("⚡ Quick cURL Test")
    print("=" * 20)
    
    endpoints = [
        ("Health", "http://localhost:8082/health"),
        ("Ready", "http://localhost:8082/ready")
    ]
    
    for name, url in endpoints:
        print(f"\nTesting {name} endpoint:")
        try:
            result = subprocess.run(
                ["curl", "-s", "--connect-timeout", "2", url],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                print(f"✅ {name}: {result.stdout[:100]}...")
            else:
                print(f"❌ {name}: No response or error")
        except Exception as e:
            print(f"❌ {name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "curl":
        quick_curl_test()
    else:
        tester = MCPServerTester()
        tester.run_tests()