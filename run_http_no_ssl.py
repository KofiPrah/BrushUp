#!/usr/bin/env python3
"""
Simple HTTP-only server for Art Critique
Uses gunicorn without SSL for Replit's load balancer
"""
import os
import sys

def configure_for_http():
    """Setup environment for HTTP mode"""
    os.environ["SSL_ENABLED"] = "false"
    os.environ["HTTP_ONLY"] = "true"
    os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
    print("Environment configured for HTTP mode")
    return True

if __name__ == "__main__":
    # Configure environment
    configure_for_http()
    
    # Start HTTP server
    cmd = "gunicorn --bind 0.0.0.0:5000 --reload main:app"
    print(f"Starting server: {cmd}")
    os.system(cmd)