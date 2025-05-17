"""
HTTP-only settings for Django/Flask.
This module configures the application for HTTP mode, which is needed
for compatibility with Replit's load balancer.

Import this module before importing Django settings.
"""
import os
import sys

# Configure environment for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# Print a message to indicate HTTP mode is active
print("HTTP server settings applied: SSL is disabled")