"""
Gunicorn configuration file for HTTP mode without SSL
"""
import os

# Use HTTP, not HTTPS
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Configure Django settings module
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# Gunicorn settings
bind = "0.0.0.0:5000"
workers = 1
timeout = 120
reload = True
reload_extra_files = ["static/"]

# Disable SSL for HTTP-only mode
certfile = None
keyfile = None

# Pre-load the app
preload_app = True

# Set the worker class
worker_class = "sync"