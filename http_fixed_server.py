#!/usr/bin/env python3
"""
Fixed HTTP-only server for Brush Up application in Replit

This script runs Django without SSL certificates to work properly in Replit's environment
"""
import os
import sys
import subprocess
from flask import Flask, redirect, request, Response

# Create Flask app
app = Flask(__name__)

# Set Django environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Django process
django_process = None

def start_django():
    """Start Django server on a local port"""
    global django_process
    if django_process is None or django_process.poll() is not None:
        print("Starting Django server...")
        django_process = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        # Give Django time to start
        import time
        time.sleep(2)
        print("Django server started")

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy requests to Django"""
    start_django()
    
    # Target Django server
    target_url = f"http://127.0.0.1:8000/{path}"
    
    # Forward request headers
    headers = {key: value for key, value in request.headers.items() 
               if key.lower() not in ('host',)}
    
    try:
        # Forward the request to Django
        import requests
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            params=request.args,
            allow_redirects=False
        )
        
        # Create Flask response
        response = Response(resp.content, resp.status_code)
        
        # Forward response headers
        for key, value in resp.headers.items():
            if key.lower() not in ('content-length', 'transfer-encoding', 'connection'):
                response.headers[key] = value
                
        return response
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    # Start Django in the background
    start_django()
    
    # Run Flask app without SSL
    print("Starting Brush Up in HTTP mode...")
    app.run(host='0.0.0.0', port=5000)