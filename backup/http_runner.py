#!/usr/bin/env python3
"""
Simple HTTP wrapper for Brush Up application
This script creates a simple HTTP server that works in Replit's environment
"""
import os
import sys
import subprocess
from flask import Flask, request, redirect, Response
import requests

# Create Flask app
app = Flask(__name__)

# Configure Django settings
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
os.environ["SSL_ENABLED"] = "false"

# Django server port
DJANGO_PORT = 8000

# Start Django process
django_process = None

def start_django():
    """Start Django server on separate port"""
    global django_process
    
    # Run Django on port 8000
    cmd = ["python", "manage.py", "runserver", f"127.0.0.1:{DJANGO_PORT}"]
    print(f"Starting Django with command: {' '.join(cmd)}")
    
    django_process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # Print output for debugging
    print(f"Django server started on port {DJANGO_PORT}")

# Routes
@app.route('/')
def index():
    """Redirect to the main application"""
    return redirect('/critique/')

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    """Forward requests to Django"""
    django_url = f'http://127.0.0.1:{DJANGO_PORT}/{path}'
    
    # Headers to forward
    headers = {key: value for key, value in request.headers.items() 
               if key.lower() not in ('host', 'connection')}
    
    # Forward the request with appropriate method
    try:
        if request.method == 'GET':
            response = requests.get(django_url, 
                                  params=request.args,
                                  headers=headers,
                                  cookies=request.cookies,
                                  allow_redirects=False)
        elif request.method == 'POST':
            response = requests.post(django_url,
                                   data=request.form,
                                   headers=headers,
                                   cookies=request.cookies,
                                   allow_redirects=False)
        elif request.method == 'PUT':
            response = requests.put(django_url,
                                  data=request.form,
                                  headers=headers,
                                  cookies=request.cookies,
                                  allow_redirects=False)
        elif request.method == 'DELETE':
            response = requests.delete(django_url,
                                     headers=headers,
                                     cookies=request.cookies,
                                     allow_redirects=False)
        else:
            return f"Method {request.method} not supported", 405
        
        # Forward response headers
        resp = Response(response.content, status=response.status_code)
        for key, value in response.headers.items():
            if key.lower() not in ('connection', 'transfer-encoding'):
                resp.headers[key] = value
                
        return resp
    
    except requests.RequestException as e:
        return f"Error proxying to Django: {str(e)}", 500

if __name__ == '__main__':
    # Start Django in the background
    start_django()
    
    # Wait a bit for Django to start
    import time
    time.sleep(2)
    
    # Start Flask app (used by gunicorn)
    print("Starting HTTP proxy for Brush Up")
    
    # Make app available for gunicorn
    if "gunicorn" not in sys.argv[0]:
        app.run(host="0.0.0.0", port=5000)
    else:
        # Gunicorn will use this app object
        pass