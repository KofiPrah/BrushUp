"""
A Simple WSGI HTTP server for Django using Gunicorn without SSL.
"""
import os

# Set environment variables for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# Import Django WSGI application
from artcritique.wsgi import application

# For Gunicorn
app = application

# These are the server settings
bind = "0.0.0.0:8000"
workers = 1
reload = True
# No SSL
certfile = None
keyfile = None