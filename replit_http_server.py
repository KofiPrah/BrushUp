"""
Simple HTTP server for Brush Up application in Replit

This script creates empty SSL certificate files (so the workflow doesn't error)
but runs the Django application without requiring them.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the Django server in HTTP mode"""
    print("Starting Brush Up application in HTTP mode...")
    
    # Create empty certificate files if they don't exist
    cert_file = Path("cert.pem")
    key_file = Path("key.pem")
    
    if not cert_file.exists():
        print("Creating empty cert.pem")
        cert_file.touch()
    
    if not key_file.exists():
        print("Creating empty key.pem")
        key_file.touch()
    
    # Run the Django server with explicit HTTP settings
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
    
    server_cmd = ["python", "manage.py", "runserver", "0.0.0.0:5000"]
    print(f"Starting server with command: {' '.join(server_cmd)}")
    
    subprocess.run(server_cmd, env=env)

if __name__ == "__main__":
    main()