#!/usr/bin/env python3
"""
HTTP-only Gunicorn configuration for Brush Up application
Explicitly disables SSL certificate requirements
"""

# Basic server configuration
bind = "0.0.0.0:5000"
workers = 3
timeout = 120
keepalive = 5
reuse_port = True
reload = True

# SSL is intentionally not configured
keyfile = None
certfile = None
ca_certs = None

# Configure HTTP mode
proxy_protocol = False
forwarded_allow_ips = "*"

# Import the main app
wsgi_app = "main:app"