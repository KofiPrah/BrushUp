"""
HTTP proxy server for Brush Up application
Creates a Flask app that proxies requests to the Django server
"""
import os
import sys
import subprocess
import socket
import time
import logging
import signal
import threading
from flask import Flask, request, Response
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Target Django server
DJANGO_HOST = "127.0.0.1"
DJANGO_PORT = 8000
PROXY_PORT = 5000

django_process = None

def start_django():
    """Start Django server in the background"""
    logger.info("Starting Django server on port %s", DJANGO_PORT)
    
    # Use Django's development server directly - no SSL needed
    cmd = [
        sys.executable,
        'manage.py',
        'runserver',
        f'{DJANGO_HOST}:{DJANGO_PORT}',
    ]
    
    # Set environment variables
    env = os.environ.copy()
    env['SSL_ENABLED'] = 'false'
    
    # Start Django process
    global django_process
    django_process = subprocess.Popen(cmd, env=env)
    
    # Wait for Django to start
    for _ in range(30):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((DJANGO_HOST, DJANGO_PORT))
            s.close()
            logger.info("Django server started successfully")
            return True
        except socket.error:
            time.sleep(1)
    
    logger.error("Failed to start Django server")
    return False

def signal_handler(sig, frame):
    """Handle termination signals"""
    logger.info("Shutting down servers...")
    if django_process:
        django_process.terminate()
        django_process.wait()
    sys.exit(0)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'])
def proxy(path):
    """Proxy all requests to Django"""
    url = f'http://{DJANGO_HOST}:{DJANGO_PORT}/{path}'
    
    # Forward request headers
    headers = {key: value for key, value in request.headers if key != 'Host'}
    
    # Forward request parameters and body
    data = request.get_data()
    cookies = request.cookies
    
    try:
        # Forward the request to Django
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=data,
            cookies=cookies,
            params=request.args,
            stream=True,
            allow_redirects=False
        )
        
        # Create Flask response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = {
            name: value for name, value in response.raw.headers.items()
            if name.lower() not in excluded_headers
        }
        
        # Handle redirects properly
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get('Location', '')
            if location.startswith(f'http://{DJANGO_HOST}:{DJANGO_PORT}'):
                # Replace Django URL with proxy URL
                location = location.replace(f'http://{DJANGO_HOST}:{DJANGO_PORT}', '')
                response_headers['Location'] = location
        
        # Return the proxied response
        proxy_response = Response(
            response.content,
            response.status_code,
            response_headers
        )
        return proxy_response
    
    except requests.RequestException as e:
        logger.error("Proxy error: %s", e)
        return Response(f"Proxy Error: {e}", 500)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy'}

if __name__ == '__main__':
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Django server in a separate thread
    django_thread = threading.Thread(target=start_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Wait for Django to start
    time.sleep(2)
    
    # Start Flask server
    logger.info("Starting HTTP proxy server on port %s", PROXY_PORT)
    app.run(host='0.0.0.0', port=PROXY_PORT)