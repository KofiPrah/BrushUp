"""
HTTP Proxy for Brush Up application
------------------------------------
This script:
1. Fixes the CritiqueSerializer
2. Sets up a proxy to handle HTTP requests and forward them to the Django app
"""
import os
import sys
import django
import subprocess
import time
import signal
import threading

from flask import Flask, request, Response, redirect

# Set up environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTPS'] = 'off'
os.environ['HTTP_ONLY'] = 'true'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Fix CritiqueSerializer
try:
    from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer
    
    # Define the missing method
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
    
    # Add method to both serializers if needed
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count method to CritiqueSerializer")
    
    if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
        setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count method to CritiqueListSerializer")
    
    print("✓ Serializer fixes applied successfully")
except Exception as e:
    print(f"! Error fixing serializers: {e}")

# Stop any existing servers
def kill_processes():
    try:
        subprocess.run(["pkill", "-f", "runserver"], check=False)
        time.sleep(1)
    except:
        pass

# Create Flask app
app = Flask(__name__)

# Django process
django_process = None
django_port = 8000

def start_django():
    """Start Django development server"""
    global django_process
    kill_processes()
    
    if django_process:
        try:
            os.kill(django_process.pid, signal.SIGTERM)
            time.sleep(1)
        except:
            pass
    
    cmd = [sys.executable, "manage.py", "runserver", "--noreload", f"127.0.0.1:{django_port}"]
    django_process = subprocess.Popen(cmd)
    print(f"✓ Started Django server on port {django_port}")
    
    # Give Django time to start
    time.sleep(2)

@app.route('/')
def index():
    """Redirect to Django app"""
    return redirect(f'http://127.0.0.1:{django_port}/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    """Proxy requests to Django"""
    import requests
    
    # Build URL with query parameters
    url = f'http://127.0.0.1:{django_port}/{path}'
    if request.query_string:
        url += f'?{request.query_string.decode()}'
    
    # Forward the request
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        
        # Create response
        response = Response(resp.content, resp.status_code)
        
        # Add headers
        for key, value in resp.headers.items():
            if key.lower() not in ('content-length', 'transfer-encoding', 'connection'):
                response.headers[key] = value
                
        return response
    except Exception as e:
        return str(e), 500

def restart_django_if_needed():
    """Check if Django is running and restart if needed"""
    global django_process
    
    if django_process is None or django_process.poll() is not None:
        start_django()

# Start Django when Flask starts
start_django()

# Create monitor thread to keep Django running
def monitor_django():
    while True:
        restart_django_if_needed()
        time.sleep(10)

monitor_thread = threading.Thread(target=monitor_django, daemon=True)
monitor_thread.start()

if __name__ == '__main__':
    # Run Flask app in HTTP mode
    app.run(host='0.0.0.0', port=5000)