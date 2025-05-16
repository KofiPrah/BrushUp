#!/usr/bin/env python
"""
Update the workflow configuration to run in HTTP mode.
This script modifies the .replit file to use HTTP mode.
"""

import os
import sys
import logging
import json
import subprocess

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_http_workflow_script():
    """Create a script to run in the workflow"""
    script_path = "run_http_workflow.py"
    
    with open(script_path, "w") as f:
        f.write("""#!/usr/bin/env python
'''
Run the application in HTTP mode for the Replit workflow.
This script is designed to be used in the workflow configuration.
'''

import os
import sys
import subprocess

# Set environment variables for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["SECURE_SSL_REDIRECT"] = "false"
os.environ["USE_S3"] = "True"

print("Starting Art Critique in HTTP mode...")
print("Running in HTTP mode (SSL handled by Replit's load balancer)")

# Command to run Gunicorn with HTTP configuration
cmd = [
    "gunicorn",
    "--bind", "0.0.0.0:5000",
    "--worker-class", "sync",
    "--workers", "1",
    "--access-logfile", "-",
    "--error-logfile", "-",
    "--reload",
    "--reuse-port",
    "main:app"
]

try:
    # Execute the command
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"Failed to start HTTP server: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("Shutting down...")
    sys.exit(0)
""")
    
    os.chmod(script_path, 0o755)  # Make executable
    return script_path

def create_run_script():
    """Create a shell script to run the application in HTTP mode"""
    script_path = "run_http_mode.sh"
    
    with open(script_path, "w") as f:
        f.write("""#!/bin/bash
# Run the Art Critique application in HTTP mode

# Set environment variables
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false
export USE_S3=True

# Stop any existing server
pkill -f gunicorn || echo "No existing server processes"

# Start Gunicorn in HTTP mode
echo "Starting Art Critique in HTTP mode..."
echo "Running in HTTP mode (SSL handled by Replit's load balancer)"

exec gunicorn --bind 0.0.0.0:5000 --worker-class sync --workers 1 --reload --reuse-port main:app
""")
    
    os.chmod(script_path, 0o755)  # Make executable
    return script_path

def main():
    """Update the workflow configuration"""
    # Create the workflow script
    workflow_script = create_http_workflow_script()
    logger.info(f"Created workflow script: {workflow_script}")
    
    # Create the run script
    run_script = create_run_script()
    logger.info(f"Created run script: {run_script}")
    
    # Print instructions
    print("\nTo update the workflow configuration:")
    print("1. In the Replit interface, click on 'Tools' in the left sidebar")
    print("2. Select 'Workflows'")
    print("3. Edit the 'Start application' workflow")
    print("4. Change the command to:")
    print(f"   python {workflow_script}")
    print("\nAlternatively, you can run the application manually with:")
    print(f"   ./{run_script}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())