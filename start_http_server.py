#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application in Replit environment
"""
import os
import sys
import subprocess
from flask import Flask, request, Response

# Set environment variables to run in HTTP mode without SSL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['DJANGO_DEBUG'] = 'true'

# Create Flask app
app = Flask(__name__)

# Django server port (internal)
DJANGO_PORT = 8000
django_process = None

def start_django():
    """Start Django server on a local port"""
    global django_process
    if django_process is None or django_process.poll() is not None:
        print("Starting Django server...")
        django_process = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", f"127.0.0.1:{DJANGO_PORT}"],
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT
        )
        print("Django server started")

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    """Proxy all requests to Django"""
    # Make sure Django is running
    start_django()
    
    # Forward the request to Django
    url = f'http://127.0.0.1:{DJANGO_PORT}/{path}'
    
    # Get query string parameters
    params = request.args.to_dict()
    
    # Forward headers
    headers = {key: value for key, value in request.headers.items() 
               if key.lower() not in ['host', 'content-length']}
    
    try:
        # Forward the request to Django with the correct method
        import requests
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=params,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        
        # Create Flask response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in resp.headers.items()
                   if name.lower() not in excluded_headers]
        
        response = Response(resp.content, resp.status_code, headers)
        return response
    except Exception as e:
        print(f"Proxy error: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    try:
        # Start Django in the background
        start_django()
        
        # Run Flask app to proxy requests
        print("Starting Brush Up in HTTP mode...")
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # Clean up Django process
        if django_process and django_process.poll() is None:
            django_process.terminate()