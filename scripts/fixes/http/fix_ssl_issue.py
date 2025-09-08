#!/usr/bin/env python3
"""
Fix SSL/HTTP issues in the Art Critique application.

This script creates a workflow-compatible version of the server
that runs without SSL certificates, which is required for proper
operation with Replit's load balancer.
"""
import os
import shutil
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def create_http_startup_script():
    """Create an HTTP-only startup script"""
    print_header("Creating HTTP startup script")
    
    script_content = """#!/bin/bash
# Start the Art Critique application in HTTP-only mode
# This script is designed for Replit's load balancer

# Set environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true
export PYTHONUNBUFFERED=1

# Run Gunicorn without SSL certificates
echo "Starting Art Critique in HTTP mode (SSL handled by Replit's load balancer)..."
exec gunicorn --bind 0.0.0.0:5000 --workers=1 --threads=2 --reload main:app
"""
    
    # Write the script to a file
    script_path = "start_http.sh"
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    print(f"Created {script_path}")
    
    # Create a symbolic link for workflow use
    symlink_path = "replit_http.sh"
    if os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(script_path, symlink_path)
    print(f"Created symlink {symlink_path} -> {script_path}")
    
    return True

def create_fixed_wsgi_app():
    """Create a fixed WSGI application for HTTP mode"""
    print_header("Creating fixed WSGI application")
    
    # Create backup of original main.py if needed
    backup_path = "main.py.original"
    if not os.path.exists(backup_path) and os.path.exists("main.py"):
        shutil.copy("main.py", backup_path)
        print(f"Created backup of main.py as {backup_path}")
    
    # Create the patched main.py
    patched_content = """import os
from artcritique.wsgi import application
from flask import Flask, redirect

# Force HTTP mode for compatibility with Replit's load balancer
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# For Gunicorn - Django WSGI Application
app = application

# Also provide a Flask application to handle specific routes
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    \"\"\"Redirect to the Django app\"\"\"
    return redirect('/admin/')

@flask_app.route('/health')
def health():
    \"\"\"Health check endpoint\"\"\"
    return {"status": "healthy"}

print("USE_S3 is", os.environ.get("USE_S3", "False"))
print("Using S3 storage:", "artcritique.storage_backends.PublicMediaStorage with bucket policy (no ACLs)" if os.environ.get("USE_S3") == "True" else "Local storage")
print("Running in HTTP mode (SSL handled by Replit's load balancer)")
"""
    
    with open("main.py", "w") as f:
        f.write(patched_content)
    
    print("Updated main.py to force HTTP mode")
    return True

def create_workflow_instructions():
    """Create instructions for updating the workflow"""
    print_header("Creating workflow instructions")
    
    instructions = """# How to Fix the SSL/HTTP Issue

## Problem
The application is currently configured to use SSL certificates (HTTPS), but
Replit's load balancer already handles SSL termination before requests reach
our application. This causes "Invalid request: HTTP_REQUEST" errors.

## Solution
You need to reconfigure the Replit workflow to use HTTP mode:

1. Open the `.replit` file in the Replit editor
2. Find this section:
   ```
   [[workflows.workflow.tasks]]
   task = "shell.exec"
   args = "gunicorn --bind 0.0.0.0:5000 --certfile=certs/cert.pem --keyfile=certs/key.pem --reuse-port --reload main:app"
   waitForPort = 5000
   ```

3. Change it to:
   ```
   [[workflows.workflow.tasks]]
   task = "shell.exec"
   args = "./start_http.sh"
   waitForPort = 5000
   ```

4. Save the file and restart the workflow

## Alternative: Run HTTP Server Manually
If you can't edit the `.replit` file, you can run the HTTP server manually:

1. Stop the current workflow
2. In the Shell, run:
   ```
   ./start_http.sh
   ```

## Files Created by This Script
- `start_http.sh`: Script to start the HTTP server
- `replit_http.sh`: Symbolic link for workflow use
- `main.py`: Updated to force HTTP mode
- `main.py.original`: Backup of the original main.py (if created)

"""
    
    # Write the instructions to a file
    instructions_path = "FIX_SSL_ISSUE.md"
    with open(instructions_path, "w") as f:
        f.write(instructions)
    
    print(f"Created instructions at {instructions_path}")
    
    # Also add to docs folder
    docs_path = "docs/replit/SSL_HTTP_FIX.md"
    os.makedirs(os.path.dirname(docs_path), exist_ok=True)
    with open(docs_path, "w") as f:
        f.write(instructions)
    
    print(f"Added instructions to documentation: {docs_path}")
    return True

def main():
    """Main function to fix SSL/HTTP issues"""
    print_header("Art Critique HTTP Fix Tool")
    print("This script will fix SSL/HTTP issues by setting up an HTTP-only configuration.")
    
    success = True
    success = success and create_http_startup_script()
    success = success and create_fixed_wsgi_app()
    success = success and create_workflow_instructions()
    
    if success:
        print_header("Success!")
        print("All files have been created successfully.")
        print("To start the application in HTTP mode, run: ./start_http.sh")
        print("For more information, see: FIX_SSL_ISSUE.md")
    else:
        print_header("Error")
        print("There was an error creating the files.")
        print("Please check the output for details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())