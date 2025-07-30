#!/usr/bin/env python3

import http.server
import socketserver
import json

class HeaderHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        print('=== Headers from Open WebUI ===')
        for header, value in self.headers.items():
            print(f'{header}: {value}')
        print('================================')
        
        # Send back a dummy response
        response = {'choices': [{'message': {'content': 'test response'}}]}
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
if __name__ == "__main__":
    with socketserver.TCPServer(('', 8001), HeaderHandler) as httpd:
        print('Test server running on http://localhost:8001')
        print('Configure Open WebUI to point to this endpoint to see headers')
        httpd.serve_forever()