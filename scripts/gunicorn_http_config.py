#!/usr/bin/env python
"""
Gunicorn configuration for HTTP mode (no SSL)
This configuration is generated for use with Replit's load balancer.
"""

import os
import multiprocessing

# Basic Gunicorn config variables
bind = "0.0.0.0:5000"
workers = 1
reload = True
reuse_port = True
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"

# HTTP-only mode (no SSL)
certfile = None
keyfile = None

# SSL settings
ssl_version = None  # Disable SSL
do_handshake_on_connect = False

# Pre-startup configuration
def on_starting(server):
    """Set environment variables before server starts"""
    os.environ["SSL_ENABLED"] = "false"
    os.environ["SECURE_SSL_REDIRECT"] = "false"
    
    # Force Django to use HTTP
    os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
    
    # Print helpful message
    print("Running in HTTP mode (SSL handled by Replit's load balancer)")
