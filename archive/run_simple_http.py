#!/usr/bin/env python3
"""
Simple HTTP server for Brush Up application
This runs a Flask app to serve HTTP requests on port 5000
"""
import os
import subprocess
import threading
import time
from flask import Flask, redirect, Response, request
from flask_cors import CORS
import requests

# Create Flask app
app = Flask(__name__)
CORS(app)

# Set environment variables
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Start Django in background
django_process = None

def start_django():
    """Start Django server in background"""
    global django_process
    cmd = ["python", "manage.py", "runserver", "8080"]
    print(f"Starting Django with command: {' '.join(cmd)}")
    django_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    print("Django started on port 8080")

# Basic routes
@app.route('/')
def index():
    """Redirect to Django app"""
    return redirect('http://localhost:8080/critique/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK'

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    """Proxy all requests to Django"""
    url = f'http://localhost:8080/{path}'
    
    # Forward the request to Django
    if request.method == 'GET':
        resp = requests.get(url, params=request.args)
    elif request.method == 'POST':
        resp = requests.post(url, data=request.form)
    elif request.method == 'PUT':
        resp = requests.put(url, data=request.form)
    elif request.method == 'DELETE':
        resp = requests.delete(url)
    else:
        return 'Method not supported', 405
    
    # Return the response
    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get('content-type', 'text/html')
    )

if __name__ == '__main__':
    # Start Django in a separate thread
    django_thread = threading.Thread(target=start_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Wait for Django to start
    time.sleep(3)
    
    # Start Flask
    print("Starting HTTP server for Brush Up on port 5000")
    app.run(host='0.0.0.0', port=5000)