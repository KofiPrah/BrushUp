"""
Simple script to run the application in HTTP mode without SSL.
This helps with the Replit environment which handles SSL termination at the load balancer.
"""
import os
from flask import Flask, redirect
from artcritique.wsgi import application as django_app
from werkzeug.middleware.proxy_fix import ProxyFix

# Create a Flask app
app = Flask(__name__)

# Apply proxy fix to handle SSL termination at the load balancer
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Setup redirects to Django app
@app.route('/')
def index():
    """Redirect to the Django app"""
    return redirect('/critique/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "mode": "HTTP"}, 200

# Add the Django app as a WSGI middleware
app.wsgi_app = django_app

if __name__ == '__main__':
    # Force HTTP mode
    os.environ['SSL_ENABLED'] = 'false'
    os.environ['HTTP_ONLY'] = 'true'
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)