"""
HTTP server for Brush Up that works in Replit environment

This script runs Django without SSL certificates
"""
import os
import sys
import subprocess
from flask import Flask, request, redirect, Response
import requests

# Set environment variable to indicate we're running in HTTP mode
os.environ['HTTP_MODE'] = 'True'
os.environ['SSL_ENABLED'] = 'False'

# Create a Flask app to handle HTTP requests
app = Flask(__name__)

# Django server port (internal)
DJANGO_PORT = 8000

# Start Django server as a subprocess
def start_django():
    """Start Django server on a local port"""
    django_process = subprocess.Popen([
        'python', 'manage.py', 'runserver', 
        f'127.0.0.1:{DJANGO_PORT}'
    ])
    return django_process

# Start Django
django_process = start_django()

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK', 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy requests to Django"""
    # Forward the request to Django
    url = f'http://127.0.0.1:{DJANGO_PORT}/{path}'
    
    # Get query string parameters
    params = {}
    for key, value in request.args.items():
        params[key] = value
    
    # Forward headers
    headers = {}
    for key, value in request.headers:
        if key.lower() not in ['host', 'content-length']:
            headers[key] = value
    
    # Make request to Django
    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        params=params,
        data=request.data,
        cookies=request.cookies,
        allow_redirects=False
    )
    
    # Create response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    
    response = Response(resp.content, resp.status_code, headers)
    
    return response

if __name__ == "__main__":
    try:
        # Run Flask app
        app.run(host='0.0.0.0', port=5000)
    finally:
        # Terminate Django process on exit
        django_process.terminate()