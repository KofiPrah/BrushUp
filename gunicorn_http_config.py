"""
Gunicorn configuration file for HTTP mode (no SSL).
This configuration is specifically designed for use with Replit's load balancer,
which handles SSL termination before requests reach the application.
"""

import os
import multiprocessing

# Bind to all interfaces on port 5000
bind = '0.0.0.0:5000'

# Number of worker processes
workers = 1

# Reload when code changes (development setting)
reload = True

# Reuse port to avoid "Address already in use" errors on restart
reuse_port = True

# Timeouts (in seconds)
timeout = 120
graceful_timeout = 30
keepalive = 2

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'

# Set working directory to project root
chdir = os.path.dirname(os.path.abspath(__file__))

# Pre-load application to catch syntax errors
preload_app = True

# SSL configuration - explicitly disabled
keyfile = None
certfile = None