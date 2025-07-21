#!/usr/bin/env python3
"""
Simple web demo for Bloomberg volatility surface
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'api'))

from multi_tenor_client import MultiTenorVolatilityClient

class VolatilityHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('templates/simple_index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path.startswith('/api/volatility/'):
            self.handle_api_request()
        else:
            super().do_GET()
    
    def handle_api_request(self):
        currency = self.path.split('/')[-1]
        
        try:
            client = MultiTenorVolatilityClient()
            df = client.get_multi_tenor_surface(currency, ["1W", "1M", "3M", "6M", "1Y"])
            
            # Create matrix
            matrix = client.create_full_delta_matrix(df)
            
            # Convert to list of dicts, handling None values
            data = []
            for _, row in matrix.iterrows():
                row_dict = {}
                for col, val in row.items():
                    if pd.isna(val) or val is None:
                        row_dict[col] = None
                    else:
                        row_dict[col] = float(val) if isinstance(val, (int, float)) else val
                data.append(row_dict)
            
            response = json.dumps({
                "success": True,
                "data": data
            })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"success": False, "error": str(e)})
            self.wfile.write(response.encode())

if __name__ == '__main__':
    import pandas as pd
    
    # Create simple template
    os.makedirs('templates', exist_ok=True)
    
    print("Starting simple Bloomberg volatility web server...")
    print("Open http://localhost:8001 in your browser")
    
    server = HTTPServer(('localhost', 8001), VolatilityHandler)
    server.serve_forever()