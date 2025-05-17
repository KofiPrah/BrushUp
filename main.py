import os
import sys

# Force HTTP mode for compatibility with Replit's load balancer
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# For Gunicorn - Django WSGI Application
from artcritique.wsgi import application
app = application

# Add the django-mathfilters to installed apps in Django settings
# This is to ensure we can use the 'mul' filter in templates
from django.conf import settings
if 'mathfilters' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
    settings.INSTALLED_APPS.append('mathfilters')
    print("Added mathfilters to INSTALLED_APPS")

from flask import Flask, redirect

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
