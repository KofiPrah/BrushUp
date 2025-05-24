"""
Simple HTTP Flask server that proxies requests to Django

This avoids SSL certificate issues by using a Flask proxy server
"""

import os
import sys
import subprocess
import signal
import time
from flask import Flask, request, Response
import requests

# Global variables
django_process = None
app = Flask(__name__)

def start_django():
    """Start Django server on port 8000"""
    global django_process
    
    print("Starting Django server on port 8000...")
    
    # Disable SSL certificates by creating empty ones
    try:
        if os.path.exists('cert.pem'):
            os.rename('cert.pem', 'cert.pem.bak')
        if os.path.exists('key.pem'):
            os.rename('key.pem', 'key.pem.bak')
        
        with open('cert.pem', 'w') as f:
            f.write('')
        with open('key.pem', 'w') as f:
            f.write('')
    except Exception as e:
        print(f"Warning: Failed to handle SSL certificates: {e}")
    
    # Use Python to run Django with runserver
    django_process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"],
        env=os.environ.copy(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give Django time to start
    time.sleep(2)
    
    print("Django server started!")
    
    return django_process

def signal_handler(sig, frame):
    """Handle termination signals"""
    global django_process
    
    print("Shutting down...")
    
    if django_process:
        django_process.terminate()
        django_process.wait()
        print("Django server stopped")
    
    sys.exit(0)

@app.route('/')
def index():
    """Redirect to Django app"""
    return redirect_to_django('')

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK"

@app.route('/<path:path>')
def proxy(path):
    """Proxy all requests to Django"""
    return redirect_to_django(path)

def redirect_to_django(path):
    """Redirect the request to Django server"""
    target_url = f"http://localhost:8000/{path}"
    
    # Copy request headers but exclude Host
    headers = {key: value for (key, value) in request.headers if key != 'Host'}
    
    # Forward the request to Django
    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        
        # Create Flask response
        response = Response(resp.content, resp.status_code)
        
        # Copy response headers
        for key, value in resp.headers.items():
            if key.lower() not in ('content-length', 'connection', 'content-encoding'):
                response.headers[key] = value
        
        return response
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Django in the background
    django_process = start_django()
    
    # Start Flask
    print("Starting Flask proxy on port 5000...")
    app.run(host='0.0.0.0', port=5000)