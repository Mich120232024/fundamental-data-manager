#!/usr/bin/env python3
"""Simple Bloomberg API Server"""

import sys
sys.path.append(r"C:\blp\API\Python")

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import blpapi

class Bloomberg:
    def __init__(self):
        self.session = None
        self.service = None
        
    def connect(self):
        opts = blpapi.SessionOptions()
        opts.setServerHost("localhost")
        opts.setServerPort(8194)
        self.session = blpapi.Session(opts)
        
        if self.session.start() and self.session.openService("//blp/refdata"):
            self.service = self.session.getService("//blp/refdata")
            return True
        return False
    
    def get_price(self, ticker):
        req = self.service.createRequest("ReferenceDataRequest")
        req.append("securities", ticker)
        req.append("fields", "PX_LAST")
        
        self.session.sendRequest(req)
        
        while True:
            ev = self.session.nextEvent(5000)
            for msg in ev:
                if msg.hasElement("securityData"):
                    data = msg.getElement("securityData").getValue(0)
                    if data.hasElement("fieldData"):
                        return data.getElement("fieldData").getElement("PX_LAST").getValue()
            if ev.eventType() == blpapi.Event.RESPONSE:
                break
        return None

bb = Bloomberg()
bb.connect()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "connected": bb.session is not None}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == "/api/market-data":
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            
            results = []
            for sec in body.get("securities", []):
                price = bb.get_price(sec)
                if price:
                    results.append({"security": sec, "fields": {"PX_LAST": float(price)}})
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())
        else:
            self.send_response(404)
            self.end_headers()

print("Starting Bloomberg API Server on port 8080...")
server = HTTPServer(('0.0.0.0', 8080), Handler)
server.serve_forever()