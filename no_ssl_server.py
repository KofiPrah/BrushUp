"""
Simple HTTP-only server for Django

This script removes the SSL certificates and starts Django in HTTP mode.
"""
import os
import sys
import subprocess
import time

def main():
    """Run Django in HTTP mode without SSL"""
    print("Setting up HTTP-only environment...")
    
    # Move existing SSL certificates out of the way if they exist
    try:
        if os.path.exists("cert.pem"):
            os.rename("cert.pem", "cert.pem.bak")
        if os.path.exists("key.pem"):
            os.rename("key.pem", "key.pem.bak")
    except Exception as e:
        print(f"Warning: Could not move SSL certificates: {e}")
    
    # Set environment variables
    os.environ["HTTPS"] = "off"
    os.environ["USE_SSL"] = "false"
    
    # Kill any running servers on port 5000
    print("Stopping any running servers...")
    os.system("pkill -f gunicorn || true")
    
    # Wait a moment for the port to be freed
    time.sleep(2)
    
    # Start Django using the development server
    print("Starting Django in HTTP mode...")
    cmd = [
        "python", 
        "manage.py", 
        "runserver", 
        "0.0.0.0:5000"
    ]
    
    # Run the server in the foreground
    print("Server starting on port 5000...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()