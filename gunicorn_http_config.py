"""
Gunicorn configuration file for HTTP mode
"""
import os

# Set environment variables
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Gunicorn settings
bind = "0.0.0.0:5000"
workers = 1
reload = True

# Remove certificate files
certfile = None
keyfile = None
# Use SSL=False to disable HTTPS
ssl_version = None