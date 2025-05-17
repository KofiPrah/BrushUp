#!/usr/bin/env python3
"""
Simple HTTP server for the Brush Up application (formerly Art Critique)
Works with Replit's environment without requiring SSL
"""
import os
import sys
from django.core.management import execute_from_command_line

# Configure Django settings
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
os.environ["SSL_ENABLED"] = "false"  # Force SSL off

# Start Django server
if __name__ == "__main__":
    # Set argv to use runserver on port 5000
    sys.argv = [sys.argv[0], "runserver", "0.0.0.0:5000"]
    print("Starting Brush Up in HTTP mode on port 5000...")
    execute_from_command_line(sys.argv)