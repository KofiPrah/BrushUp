#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application
"""
import os
import sys
from flask import Flask, request, redirect
import requests
import threading
import subprocess
import time

# Create a Flask app for HTTP
app = Flask(__name__)

# Global variable to track the Django process
django_process = None

def start_django():
    """Start Django server in HTTP mode"""
    global django_process
    
    # Set environment variables for Django
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    env['SSL_ENABLED'] = 'false'
    env['HTTP_ONLY'] = 'true'
    env['HTTPS'] = 'off'
    
    # Create empty certificate files if they don't exist
    for filename in ['cert.pem', 'key.pem']:
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write("")
    
    # Start Django on port 8000
    cmd = [
        "python", "manage.py", "runserver", "0.0.0.0:8000"
    ]
    
    print(f"Starting Django: {' '.join(cmd)}")
    django_process = subprocess.Popen(cmd, env=env)
    
    # Wait for Django to start
    time.sleep(3)
    print("Django server started on port 8000")

@app.route('/')
def index():
    """Redirect to Django application"""
    return redirect("http://localhost:8000/")

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            return "Django server is running", 200
        else:
            return f"Django server returned status code {response.status_code}", 500
    except requests.RequestException:
        return "Django server is not running", 500

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    """Proxy all requests to Django"""
    url = f"http://localhost:8000/{path}"
    
    # Forward the request to Django
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    
    # Create response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    
    response = app.response_class(
        response=resp.content,
        status=resp.status_code,
        headers=headers)
    
    return response

if __name__ == '__main__':
    # Start Django in a separate thread
    threading.Thread(target=start_django).start()
    
    # Start Flask on port 5000
    app.run(host='0.0.0.0', port=5000)