"""
HTTP-only settings for Django.
This module modifies the Django settings to work with Replit's load balancer.
Import this module before importing Django settings.
"""

import os

# Force HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["SECURE_SSL_REDIRECT"] = "false"

# Use S3 for storage
os.environ["USE_S3"] = "True"

# Print a message
print("Applied HTTP-only settings (SSL handled by Replit's load balancer)")