#!/usr/bin/env python3
"""
Simple Flask HTTP-only proxy for Brush Up application
"""
import os
import subprocess
import time
import signal
import sys
from flask import Flask, request, redirect, Response
import requests

# Django server configuration
DJANGO_HOST = "127.0.0.1"
DJANGO_PORT = 8000
FLASK_PORT = 5000

# Create Flask app
app = Flask(__name__)
django_process = None

def start_django():
    """Start Django server on port 8000"""
    # Set environment variables
    env = os.environ.copy()
    env["SSL_ENABLED"] = "false"
    env["HTTP_ONLY"] = "true" 
    env["HTTPS"] = "off"
    env["wsgi.url_scheme"] = "http"
    env["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
    
    # Start Django on port 8000
    cmd = ["python", "manage.py", "runserver", f"{DJANGO_HOST}:{DJANGO_PORT}"]
    process = subprocess.Popen(cmd, env=env)
    
    # Wait for Django to start
    time.sleep(3)
    return process

def signal_handler(sig, frame):
    """Handle termination signals"""
    print("\nShutting down...")
    if django_process:
        django_process.terminate()
    sys.exit(0)

@app.route('/health')
def health():
    """Health check endpoint"""
    return "Flask proxy server is running"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy all requests to Django"""
    target_url = f"http://{DJANGO_HOST}:{DJANGO_PORT}/{path}"
    
    # Forward the request to Django
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        params=request.args
    )
    
    # Build response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for name, value in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    
    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Django server
    print("Starting Django server...")
    django_process = start_django()
    
    try:
        # Start Flask proxy server
        print(f"Starting Flask proxy on port {FLASK_PORT}...")
        app.run(host='0.0.0.0', port=FLASK_PORT)
    finally:
        if django_process:
            django_process.terminate()