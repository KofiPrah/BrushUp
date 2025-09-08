#!/usr/bin/env python3
"""
HTTP Server for Brush Up application
This version runs without SSL certificates
"""
import os
import subprocess

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Apply serializer fixes if needed
try:
    from fix_critique_serializer import add_missing_method
    add_missing_method()
    print("✓ Applied serializer fixes")
except Exception as e:
    print(f"! Serializer fix error: {str(e)}")

def main():
    # Run gunicorn with HTTP configuration
    cmd = ["gunicorn", 
           "--bind", "0.0.0.0:5000", 
           "--reload",
           "--access-logfile", "-",
           "--error-logfile", "-",
           "wsgi:application"]
    
    print("Starting HTTP server on port 5000...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()