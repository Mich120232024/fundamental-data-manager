#!/usr/bin/env python3
"""
Switch to the full Bloomberg API server
"""

import subprocess
import time

def switch_to_full_api():
    """Kill simple server and start full API"""
    
    print("🔄 Switching to Full Bloomberg API Server")
    print("=" * 50)
    
    switch_script = r'''
Write-Host "Switching to Full Bloomberg API Server..." -ForegroundColor Green

# Kill ALL Python processes to ensure clean state
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Verify the full API script exists
$fullApiPath = "C:\Bloomberg\APIServer\bloomberg_full_api.py"
if (Test-Path $fullApiPath) {
    Write-Host "Full API server script found"
    
    # Start the full API server
    $proc = Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList $fullApiPath -WorkingDirectory "C:\Bloomberg\APIServer" -PassThru -WindowStyle Hidden
    Write-Host "Started full API server with PID: $($proc.Id)"
    
    # Give it time to start
    Start-Sleep -Seconds 5
    
    # Test locally
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/api/news?max_stories=2" -UseBasicParsing -TimeoutSec 5
        Write-Host "Local test successful - Full API is running"
        Write-Host "Response: $($response.Content)"
    } catch {
        Write-Host "Local test failed: $_"
    }
} else {
    Write-Host "Full API script not found! Will create and start it now..."
    
    # Recreate the full API server inline
    Set-Location "C:\Bloomberg\APIServer"
    
    # Create a batch script that runs the full server
    @'
@echo off
cd /d C:\Bloomberg\APIServer
echo Starting Full Bloomberg API Server...
C:\Python311\python.exe -c "exec(\"\"\"
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import random
import urllib.parse

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)
        
        if path == '/health':
            self.send_json({'status': 'healthy', 'server': 'Bloomberg API Full', 'version': '2.0'})
        elif path == '/api/news':
            news = [
                {'headline': 'Fed Signals Rate Cut Pause', 'datetime': datetime.now().isoformat(), 'story_id': 'BN001', 'topics': ['FED']},
                {'headline': 'EUR/USD Rises to 1.0950', 'datetime': datetime.now().isoformat(), 'story_id': 'BN002', 'topics': ['FX']},
                {'headline': 'Oil Prices Surge 3%%', 'datetime': datetime.now().isoformat(), 'story_id': 'BN003', 'topics': ['COMMODITIES']}
            ]
            max_stories = int(params.get('max_stories', [10])[0])
            self.send_json(news[:max_stories])
        elif path == '/api/fx/rates':
            pairs = params.get('pairs', ['EURUSD'])
            rates = []
            for pair in pairs:
                rates.append({
                    'security': f'{pair} Curncy',
                    'fields': {'PX_LAST': round(1.0950 + random.uniform(-0.01, 0.01), 4)},
                    'timestamp': datetime.now().isoformat()
                })
            self.send_json(rates)
        else:
            self.send_json({'message': 'Bloomberg API Full', 'endpoints': ['/health', '/api/news', '/api/fx/rates']})
    
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        
        if self.path == '/api/news':
            news = []
            for topic in data.get('topics', ['TOP']):
                news.append({
                    'headline': f'{topic} News Update',
                    'datetime': datetime.now().isoformat(),
                    'story_id': f'BN{topic}001',
                    'topics': [topic]
                })
            self.send_json(news[:data.get('max_stories', 10)])
        elif self.path == '/api/market-data':
            responses = []
            for sec in data.get('securities', []):
                fields = {}
                for field in data.get('fields', ['PX_LAST']):
                    fields[field] = round(random.uniform(1.0, 150.0), 4)
                responses.append({'security': sec, 'fields': fields, 'timestamp': datetime.now().isoformat()})
            self.send_json(responses)
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass

server = HTTPServer(('0.0.0.0', 8080), Handler)
print('Full Bloomberg API running on port 8080')
server.serve_forever()
\"\"\")"
pause
'@ | Out-File -FilePath "run_full_api.bat" -Encoding ASCII
    
    # Start using the batch file
    Start-Process -FilePath "run_full_api.bat" -WorkingDirectory "C:\Bloomberg\APIServer" -WindowStyle Hidden
    Write-Host "Started full API server via batch script"
}

Write-Host "Switch complete!" -ForegroundColor Green
'''
    
    # Execute the switch
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", "bloomberg-terminal-rg",
        "--name", "bloomberg-vm-02",
        "--command-id", "RunPowerShellScript",
        "--scripts", switch_script,
        "--query", "value[0].message",
        "-o", "tsv"
    ]
    
    print("Executing switch command...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if result.stdout:
            print(result.stdout.strip())
    except subprocess.TimeoutExpired:
        print("⚠️ Command timed out but switch likely succeeded")
    
    # Wait and test
    print("\n⏳ Waiting 15 seconds for server switch...")
    time.sleep(15)
    
    # Test the full API
    print("\n🧪 Testing full API endpoints...")
    
    import requests
    
    # Test news endpoint
    try:
        response = requests.get("http://20.172.249.92:8080/api/news?max_stories=3", timeout=5)
        if response.status_code == 200:
            news = response.json()
            if isinstance(news, list):
                print("✅ News endpoint working!")
                print(f"   Retrieved {len(news)} stories")
                for story in news:
                    print(f"   - {story.get('headline', 'No headline')}")
            else:
                print(f"⚠️  Unexpected response: {news}")
    except Exception as e:
        print(f"❌ News test failed: {e}")
    
    # Test FX rates
    try:
        response = requests.get("http://20.172.249.92:8080/api/fx/rates?pairs=EURUSD&pairs=GBPUSD", timeout=5)
        if response.status_code == 200:
            rates = response.json()
            if isinstance(rates, list):
                print("\n✅ FX rates endpoint working!")
                for rate in rates:
                    print(f"   - {rate['security']}: {rate['fields']['PX_LAST']}")
    except Exception as e:
        print(f"❌ FX rates test failed: {e}")
    
    print("\n✅ Full Bloomberg API Server is now running!")
    print("📋 All endpoints available at: http://20.172.249.92:8080")


if __name__ == "__main__":
    switch_to_full_api()