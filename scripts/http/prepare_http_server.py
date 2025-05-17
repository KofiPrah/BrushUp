#!/usr/bin/env python3
"""
Utility script to prepare the HTTP server configuration.
This will create a patch for the Gunicorn configuration.
"""
import os
import shutil

def create_http_gunicorn_config():
    """Create a Gunicorn configuration file for HTTP mode"""
    config_content = """
# Gunicorn configuration for HTTP mode
bind = "0.0.0.0:5000"
workers = 2
threads = 2
reload = True

def on_starting(server):
    \"\"\"Set environment variables before server starts\"\"\"
    os.environ["SSL_ENABLED"] = "false"
    os.environ["HTTP_ONLY"] = "true"
    print("Starting Gunicorn in HTTP mode (SSL handled by Replit's load balancer)")
"""
    
    # Write the configuration to a file
    with open("gunicorn_http.conf.py", "w") as f:
        f.write(config_content)
    
    print("Created Gunicorn HTTP configuration: gunicorn_http.conf.py")
    return True

def create_run_http_script():
    """Create a script to run Gunicorn with the HTTP configuration"""
    script_content = """#!/bin/bash
# Run the Django application in HTTP mode with Gunicorn
# This script uses a custom Gunicorn configuration for HTTP

# Set environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true

# Run Gunicorn with HTTP configuration
echo "Starting Django in HTTP mode (SSL handled by Replit's load balancer)..."
exec gunicorn --config gunicorn_http.conf.py main:app
"""
    
    # Write the script to a file
    with open("run_http_server.sh", "w") as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod("run_http_server.sh", 0o755)
    
    print("Created HTTP server script: run_http_server.sh")
    return True

def main():
    """Main function to set up HTTP server files"""
    print("Preparing HTTP server configuration...")
    
    # Create the necessary files
    create_http_gunicorn_config()
    create_run_http_script()
    
    print("\nHTTP server configuration complete!")
    print("To run the server in HTTP mode, execute: ./run_http_server.sh")
    
    return True

if __name__ == "__main__":
    main()