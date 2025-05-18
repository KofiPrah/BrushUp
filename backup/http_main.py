"""
HTTP server for Brush Up application
"""
import os
import django
import sys
from flask import Flask, request, Response, redirect
import requests
import subprocess
import signal
import time

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'
os.environ['HTTP_ONLY'] = 'true'
os.environ['SSL_ENABLED'] = 'false'

# Initialize Django
django.setup()

# Fix CritiqueSerializer
try:
    from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer
    
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
    
    # Add method to serializers if needed
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count to CritiqueSerializer")
    
    if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
        setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count to CritiqueListSerializer")
    
    print("✓ Successfully fixed CritiqueSerializer methods")
except Exception as e:
    print(f"! Error fixing serializers: {e}")

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "brushup-app-secret")

# Django process
django_process = None
django_port = 8000

def start_django():
    """Start Django development server"""
    global django_process
    if django_process:
        try:
            os.kill(django_process.pid, signal.SIGTERM)
        except:
            pass
    
    # Start Django
    cmd = [
        sys.executable, 'manage.py', 'runserver',
        '--noreload', f'127.0.0.1:{django_port}'
    ]
    django_process = subprocess.Popen(cmd)
    print(f"✓ Started Django server on port {django_port}")
    time.sleep(2)  # Give Django time to start

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
    # Build the URL
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

# Start Django when this script runs
start_django()

if __name__ == '__main__':
    # Run Flask in HTTP mode
    app.run(host='0.0.0.0', port=5000)