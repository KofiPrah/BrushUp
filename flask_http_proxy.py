"""
Flask HTTP proxy server for Brush Up application

This script creates a simple Flask server that proxies requests to the Django app
running on a different port, avoiding SSL certificate requirements completely.
"""
import os
import subprocess
import time
import sys
from flask import Flask, request, Response, redirect
import requests

app = Flask(__name__)
django_process = None

def start_django():
    """Start Django server on port 8000"""
    global django_process
    if django_process is None or django_process.poll() is not None:
        print("Starting Django server...")
        django_cmd = ["python", "manage.py", "runserver", "127.0.0.1:8000"]
        django_process = subprocess.Popen(django_cmd)
        # Give Django time to start up
        time.sleep(2)
        print("Django server started on port 8000")
    return django_process

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check if Django is running
        response = requests.get('http://127.0.0.1:8000/api/health/', timeout=2)
        if response.status_code == 200:
            return {"status": "ok", "message": "Django is running"}
        else:
            return {"status": "error", "message": f"Django returned status code {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": f"Error connecting to Django: {str(e)}"}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy all requests to Django server"""
    try:
        # Make sure Django is running
        start_django()
        
        # Forward the request to Django
        url = f"http://127.0.0.1:8000/{path}"
        
        # Copy request headers but remove host
        headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
        
        # Forward the request using the same HTTP method
        if request.method == 'GET':
            resp = requests.get(url, headers=headers, params=request.args, timeout=10, stream=True)
        elif request.method == 'POST':
            resp = requests.post(url, headers=headers, data=request.get_data(), timeout=10, stream=True)
        elif request.method == 'PUT':
            resp = requests.put(url, headers=headers, data=request.get_data(), timeout=10, stream=True)
        elif request.method == 'DELETE':
            resp = requests.delete(url, headers=headers, timeout=10, stream=True)
        else:
            # For other HTTP methods
            resp = requests.request(
                method=request.method,
                url=url,
                headers=headers,
                data=request.get_data(),
                params=request.args,
                timeout=10,
                stream=True
            )
        
        # Create a Flask response from the Django response
        response = Response(
            resp.iter_content(chunk_size=10*1024),
            status=resp.status_code
        )
        
        # Copy response headers except ones that cause issues
        excluded_headers = ['content-encoding', 'transfer-encoding', 'content-length']
        for key, value in resp.headers.items():
            if key.lower() not in excluded_headers:
                response.headers[key] = value
        
        return response
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Django server: {str(e)}", 500

if __name__ == '__main__':
    print("Starting Flask HTTP proxy for Django...")
    start_django()
    app.run(host='0.0.0.0', port=5000)