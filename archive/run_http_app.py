#!/usr/bin/env python3
"""
Simple HTTP Server for Brush Up application
This script runs a Flask server that proxies requests to Django without using SSL
"""
from flask import Flask, request, Response, redirect
import os
import sys
import subprocess
import requests
import time

# Configure environment for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

app = Flask(__name__)
django_process = None

def start_django():
    """Start the Django server in the background"""
    global django_process
    if django_process is None or django_process.poll() is not None:
        print("Starting Django development server...")
        # Use manage.py runserver without SSL
        django_process = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        # Wait for Django to start up
        time.sleep(2)
        print("Django server started")

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Forward all requests to Django"""
    # Make sure Django is running
    start_django()
    
    # Build the target URL
    target_url = f"http://127.0.0.1:8000/{path}"
    
    # Copy headers, excluding Host
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ('host',)
    }
    
    try:
        # Forward the request to Django
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            params=dict(request.args),  # Convert to dict to avoid compatibility issues
            allow_redirects=False
        )
        
        # Create a response to send back
        flask_response = Response(
            response.content,
            status=response.status_code
        )
        
        # Forward headers from Django response
        for key, value in response.headers.items():
            if key.lower() not in ('content-length', 'transfer-encoding', 'connection'):
                flask_response.headers[key] = value
                
        return flask_response
    except Exception as e:
        return f"Error connecting to Django: {str(e)}", 500

if __name__ == "__main__":
    # Start Django server
    start_django()
    
    # Start Flask server
    print("Starting Brush Up HTTP proxy server...")
    app.run(host='0.0.0.0', port=5000)