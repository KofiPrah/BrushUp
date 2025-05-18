#!/usr/bin/env python3
"""
Simple HTTP server for Brush Up application without SSL certificates
Using standard Django development server to avoid SSL issues
"""
import os
import sys
import subprocess

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['DJANGO_DEBUG'] = 'true'

# Print information about running in HTTP mode
print("Starting Brush Up in HTTP mode...")
print("Using HTTP server without SSL certificates")

# Run Django directly on port 5000 without SSL
try:
    # Use the Django development server directly
    command = [sys.executable, "manage.py", "runserver", "0.0.0.0:5000"]
    
    # Run Django and wait for it to complete
    process = subprocess.run(command)
    
    # Exit with the same status code as Django
    sys.exit(process.returncode)
except KeyboardInterrupt:
    print("\nServer stopped")
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)