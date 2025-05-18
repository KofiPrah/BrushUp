"""
Simple HTTP server for Art Critique (Updated version)

This script runs a pure HTTP server for the Art Critique app
without using SSL certificates, compatible with Replit's load balancer.
"""

import os
from artcritique.wsgi import application

# Force HTTP mode for compatibility with Replit's load balancer
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# For Gunicorn - Django WSGI Application
app = application

# Print startup information
print("USE_S3 is", os.environ.get("USE_S3", "False"))
print("Using S3 storage:", "artcritique.storage_backends.PublicMediaStorage with bucket policy (no ACLs)" if os.environ.get("USE_S3") == "True" else "Local storage")
print("Running in HTTP mode (SSL handled by Replit's load balancer)")