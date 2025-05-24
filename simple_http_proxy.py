"""
Simple HTTP proxy server for Django
Avoids SSL certificate issues in Replit
"""
import os
import signal
import subprocess
import sys
import time
from flask import Flask, request, Response
import requests

# Create Flask app
app = Flask(__name__)

# Django server process
django_process = None

def start_django():
    """Start Django server in the background"""
    global django_process
    
    # Set Django to run on port 8000
    cmd = [sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000']
    
    # Set environment variables for Django
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    env['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    
    # Start Django
    print("Starting Django server...")
    django_process = subprocess.Popen(cmd, env=env)
    
    # Wait for Django to start
    time.sleep(2)
    print("Django server started")

def signal_handler(sig, frame):
    """Handle termination signals"""
    if django_process:
        print("Shutting down Django server...")
        django_process.terminate()
    print("Shutting down Flask server...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy requests to Django server"""
    django_url = f"http://127.0.0.1:8000/{path}"
    
    # Forward request headers
    headers = {key: value for (key, value) in request.headers if key != 'Host'}
    
    # Forward request method, URL, headers, data
    try:
        resp = requests.request(
            method=request.method,
            url=django_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=dict(request.args)
        )
        
        # Create Flask response
        response = Response(resp.content, resp.status_code)
        
        # Forward response headers
        for key, value in resp.headers.items():
            if key.lower() not in ('content-length', 'connection', 'content-encoding'):
                response.headers[key] = value
                
        return response
    except requests.RequestException as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    # Start Django server
    start_django()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000)