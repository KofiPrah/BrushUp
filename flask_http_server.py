#!/usr/bin/env python3
"""
Simple HTTP-only Flask proxy server for Brush Up in Replit
Directly included in workflow to ensure HTTP mode
"""
import os
import subprocess
import time
import sys
from flask import Flask, request, Response, redirect

# Set environment variables for HTTP mode
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['DJANGO_DEBUG'] = 'true'

app = Flask(__name__)
DJANGO_PORT = 8000
django_process = None

def start_django():
    """Start Django server as a subprocess"""
    global django_process
    if django_process is None or django_process.poll() is not None:
        print("Starting Django development server...")
        django_process = subprocess.Popen([
            sys.executable, "manage.py", "runserver", 
            f"127.0.0.1:{DJANGO_PORT}"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Wait for Django to start
        time.sleep(2)
        print("Django server started")

# Start Django when the server starts
start_django()

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    """Proxy all requests to Django"""
    import requests
    
    # Ensure Django is running
    start_django()
    
    # Forward the request to Django
    url = f'http://127.0.0.1:{DJANGO_PORT}/{path}'
    
    # Forward headers
    headers = {k: v for k, v in request.headers.items() 
              if k.lower() not in ['host', 'content-length']}
    
    try:
        # Forward the request
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        
        # Create response
        response = Response(resp.content, resp.status_code)
        
        # Forward response headers
        for name, value in resp.headers.items():
            if name.lower() not in ['content-encoding', 'content-length', 
                                    'transfer-encoding', 'connection']:
                response.headers[name] = value
        
        return response
    except Exception as e:
        print(f"Proxy error: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    print("Starting HTTP-only server for Brush Up...")
    app.run(host='0.0.0.0', port=5000)