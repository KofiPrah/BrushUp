import os
from artcritique.wsgi import application
from flask import Flask, redirect

# Force HTTP mode for compatibility with Replit's load balancer
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# For Gunicorn - Django WSGI Application
app = application

# Also provide a Flask application to handle specific routes
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    """Redirect to the Django app"""
    return redirect('/critique/')

@flask_app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

print("USE_S3 is", os.environ.get("USE_S3", "False"))
print("Using S3 storage:", "artcritique.storage_backends.PublicMediaStorage with bucket policy (no ACLs)" if os.environ.get("USE_S3") == "True" else "Local storage")
print("Running in HTTP mode (SSL handled by Replit's load balancer)")
