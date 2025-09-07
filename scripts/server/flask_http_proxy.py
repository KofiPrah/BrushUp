"""
Flask HTTP proxy server for Brush Up application

This script creates a simple Flask server that proxies requests to the Django app
running on a different port, avoiding SSL certificate requirements completely.
"""
import os
import sys
import signal
import subprocess
import threading
import time
from flask import Flask, request, Response
import requests

# Create Flask app
app = Flask(__name__)

# Global variable for the Django process
django_process = None

def start_django():
    """Start Django server on port 8000"""
    # Set Django environment variables
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    env['PYTHONUNBUFFERED'] = '1'
    
    # Start Django server on port 8000 (internal only)
    cmd = [sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000']
    
    # Print banner
    print("\n" + "=" * 70)
    print(" BRUSH UP - DJANGO SERVER (INTERNAL) ".center(70, '='))
    print("=" * 70)
    
    return subprocess.Popen(cmd, env=env)

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\nShutting down servers...")
    if django_process:
        django_process.terminate()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'Flask HTTP proxy is running'}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy all requests to Django server"""
    django_url = f'http://127.0.0.1:8000/{path}'
    
    # Forward the request method, headers, and body
    resp = requests.request(
        method=request.method,
        url=django_url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        params=request.args
    )
    
    # Create a Flask Response object from the Django response
    response = Response(resp.content, resp.status_code)
    
    # Copy response headers
    for key, value in resp.headers.items():
        if key not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding'):
            response.headers[key] = value
    
    return response

if __name__ == '__main__':
    # Start Django in a separate process
    django_process = start_django()
    
    # Wait for Django to start
    time.sleep(2)
    
    # Print banner for Flask
    print("\n" + "=" * 70)
    print(" BRUSH UP - FLASK HTTP PROXY ".center(70, '='))
    print("=" * 70)
    print("Starting Flask proxy server on port 5000")
    
    try:
        # Start Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # Make sure to terminate Django when Flask exits
        if django_process:
            django_process.terminate()