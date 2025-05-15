#!/usr/bin/env python
"""
Simple script to run the Django application over HTTP.
This is useful for testing when SSL issues occur.
"""

import os
import subprocess
import sys

def main():
    # Set environment variable to disable SSL
    os.environ["SSL_ENABLED"] = "false"
    
    # Define the port to use
    port = 8080
    
    print(f"Starting Django server in HTTP mode on port {port}")
    print("This can be used for testing the image upload functionality")
    print("Press Ctrl+C to stop the server")
    
    # Construct the command
    cmd = [
        "python", "manage.py", "runserver", f"0.0.0.0:{port}"
    ]
    
    # Run the command
    try:
        process = subprocess.run(cmd)
        sys.exit(process.returncode)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()