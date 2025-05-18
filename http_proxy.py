"""
Flask HTTP proxy for Django application
Uses HTTP-only mode to avoid SSL certificate requirements
"""
import os
import subprocess
import time
from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Start the Django server as a subprocess
django_process = None

def start_django():
    """Start Django application in the background"""
    global django_process
    if django_process is None or django_process.poll() is not None:
        # Run Django using gunicorn on a different port
        cmd = [
            "gunicorn",
            "--bind", "127.0.0.1:8000",
            "--reload",
            "--log-level", "info",
            "artcritique.wsgi:application"
        ]
        django_process = subprocess.Popen(cmd)
        time.sleep(2)  # Give Django time to start

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "HTTP proxy is running"}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy all requests to Django"""
    # Make sure Django is running
    start_django()
    
    # Forward the request to Django
    url = f"http://127.0.0.1:8000/{path}"
    
    # Copy request headers
    headers = {k: v for k, v in request.headers.items() if k != 'Host'}
    
    # Forward the request method
    if request.method == 'GET':
        resp = requests.get(url, headers=headers, params=request.args, stream=True)
    elif request.method == 'POST':
        resp = requests.post(url, headers=headers, data=request.get_data(), stream=True)
    elif request.method == 'PUT':
        resp = requests.put(url, headers=headers, data=request.get_data(), stream=True)
    elif request.method == 'DELETE':
        resp = requests.delete(url, headers=headers, stream=True)
    else:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            stream=True
        )
    
    # Create and return the Flask response
    response = Response(
        resp.iter_content(chunk_size=10*1024),
        status=resp.status_code
    )
    
    # Copy response headers
    for key, value in resp.headers.items():
        if key.lower() not in ('content-encoding', 'transfer-encoding'):
            response.headers[key] = value
    
    return response

if __name__ == '__main__':
    print("Starting HTTP proxy for Django...")
    start_django()
    app.run(host='0.0.0.0', port=5000)