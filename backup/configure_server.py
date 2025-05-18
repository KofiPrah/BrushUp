#!/usr/bin/env python3
"""
Configuration script for Django server to work properly in Replit environment
"""
import os
import sys

def configure_server():
    """Configure server for HTTP mode in Replit environment"""
    print("Configuring server for Replit environment...")
    
    # Configure for HTTP mode
    os.environ.setdefault("SSL_ENABLED", "false")
    os.environ.setdefault("HTTP_ONLY", "true")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
    
    print("Server configured for HTTP mode")
    return True

if __name__ == "__main__":
    configure_server()