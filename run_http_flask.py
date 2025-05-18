"""
Simple HTTP Flask server that proxies requests to Django

This avoids SSL certificate issues by using a Flask proxy server
"""

import os
import sys
import subprocess
import time
import signal
from flask import Flask, request, Response, redirect
import requests

app = Flask(__name__)
django_process = None
DJANGO_PORT = 8000

def start_django():
    """Start Django server on port 8000"""
    global django_process
    
    # Set environment variables for HTTP mode
    os_env = os.environ.copy()
    os_env["SSL_ENABLED"] = "false"
    os_env["HTTP_ONLY"] = "true"
    os_env["HTTPS"] = "off"
    os_env["wsgi_url_scheme"] = "http"
    
    print("Starting Django server...")
    cmd = [sys.executable, "manage.py", "runserver", f"0.0.0.0:{DJANGO_PORT}"]
    django_process = subprocess.Popen(cmd, env=os_env)
    
    # Wait for Django to start
    time.sleep(3)
    print(f"Django server started on port {DJANGO_PORT}")

def signal_handler(sig, frame):
    """Handle termination signals"""
    print("Shutting down servers...")
    if django_process:
        django_process.terminate()
    sys.exit(0)

@app.route('/')
def index():
    """Redirect to Django app"""
    return redirect(f"http://localhost:{DJANGO_PORT}/")

@app.route('/health')
def health():
    """Health check endpoint"""
    return "HTTP Flask proxy server is running!"

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    """Proxy all requests to Django"""
    url = f"http://localhost:{DJANGO_PORT}/{path}"
    
    # Forward the request to Django
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        params=request.args
    )
    
    # Create a Flask response object
    response = Response(resp.content, resp.status_code)
    
    # Set response headers
    for key, value in resp.headers.items():
        if key.lower() not in ('content-length', 'transfer-encoding', 'content-encoding'):
            response.headers[key] = value
    
    return response

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Django in the background
    start_django()
    
    # Start Flask proxy server
    print("Starting Flask proxy server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)