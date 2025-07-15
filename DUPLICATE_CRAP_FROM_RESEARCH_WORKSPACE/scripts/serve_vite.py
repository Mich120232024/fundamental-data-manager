#!/usr/bin/env python3
"""Simple HTTP server for Vite project on port 3300"""
import http.server
import socketserver
import os
import sys

PORT = 3300
DIRECTORY = "/Users/mikaeleage/Projects Container/gzc-production-platform-vite"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

print(f"Starting server on port {PORT}")
print(f"Serving directory: {DIRECTORY}")
print(f"Access at: http://localhost:{PORT}/")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)