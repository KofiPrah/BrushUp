#!/usr/bin/env python3
"""
Main entry point for Brush Up application
Using a Flask wrapper for HTTP compatibility with Replit
"""
import os
import sys

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"

# Import HTTP wrapper app
from http_runner import app