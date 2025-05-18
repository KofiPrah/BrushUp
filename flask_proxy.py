#!/usr/bin/env python3
"""
Simple Flask HTTP proxy for Brush Up application
Uses a proxy approach that works well in Replit
"""
import os
import subprocess
import threading
import time
import requests
from flask import Flask, request, Response, redirect

# Configuration
DJANGO_HOST = "127.0.0.1"
DJANGO_PORT = 8000
FLASK_PORT = 5000

# Set environment variables for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Create Flask app
app = Flask(__name__)

# Global flag to track if Django is running
django_started = False
django_process = None

def start_django_server():
    """Start Django development server in the background"""
    global django_process
    django_process = subprocess.Popen(
        ["python", "manage.py", "runserver", f"{DJANGO_HOST}:{DJANGO_PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    # Wait for Django to start
    time.sleep(2)
    print("Django server started")

def ensure_django_running():
    """Make sure Django server is running"""
    global django_started
    if not django_started:
        django_started = True
        start_django_server()

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy all requests to Django"""
    ensure_django_running()
    
    # Build the URL for the Django server
    django_url = f"http://{DJANGO_HOST}:{DJANGO_PORT}/{path}"
    
    # Copy the request method, headers, and data to forward to Django
    method = request.method
    headers = {key: value for key, value in request.headers.items() 
               if key.lower() not in ('host', 'content-length')}
    data = request.get_data()
    
    try:
        # Forward the request to Django
        response = requests.request(
            method,
            django_url,
            headers=headers,
            data=data,
            params=request.args,
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )
        
        # Copy the response from Django
        flask_response = Response(
            response=response.raw.read(),
            status=response.status_code
        )
        
        # Copy headers from Django response
        for key, value in response.headers.items():
            if key.lower() not in ('content-encoding', 'transfer-encoding', 'content-length'):
                flask_response.headers[key] = value
                
        return flask_response
    except requests.RequestException as e:
        return f"Error connecting to Django: {str(e)}", 500

if __name__ == "__main__":
    # Start Django in a separate thread
    threading.Thread(target=ensure_django_running).start()
    
    # Start Flask server
    print("Starting Brush Up proxy server...")
    app.run(host='0.0.0.0', port=FLASK_PORT)