#!/usr/bin/env python
"""
Generate a custom Gunicorn configuration for the Art Critique application
that only uses HTTP (no SSL) and works with Replit's load balancer.

This script creates a new configuration file that can be used to run
the server properly when working with Replit.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration template
GUNICORN_CONFIG_TEMPLATE = """#!/usr/bin/env python
\"\"\"
Gunicorn configuration for HTTP mode (no SSL)
This configuration is generated for use with Replit's load balancer.
\"\"\"

import os
import multiprocessing

# Basic Gunicorn config variables
bind = "0.0.0.0:5000"
workers = 1
reload = True
reuse_port = True
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"

# HTTP-only mode (no SSL)
certfile = None
keyfile = None

# Pre-startup configuration
def on_starting(server):
    \"\"\"Set environment variables before server starts\"\"\"
    os.environ["SSL_ENABLED"] = "false"
    os.environ["SECURE_SSL_REDIRECT"] = "false"
    print("Running in HTTP mode (SSL handled by Replit's load balancer)")
"""

def main():
    """Generate the HTTP Gunicorn configuration"""
    output_file = "gunicorn_http_config.py"
    
    logger.info(f"Generating HTTP Gunicorn configuration: {output_file}")
    
    with open(output_file, "w") as f:
        f.write(GUNICORN_CONFIG_TEMPLATE)
    
    os.chmod(output_file, 0o755)  # Make executable
    
    logger.info(f"Configuration generated successfully: {output_file}")
    logger.info("You can now run the server with:")
    logger.info(f"  gunicorn -c {output_file} main:app")
    
    # Create a wrapper script
    wrapper_script = "run_http_flask.sh"
    with open(wrapper_script, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# Run the Art Critique application in HTTP mode\n")
        f.write("\n")
        f.write("# Stop any existing server\n")
        f.write("pkill -f gunicorn || echo \"No existing server processes\"\n")
        f.write("\n")
        f.write("# Set environment variables\n")
        f.write("export SSL_ENABLED=false\n")
        f.write("export SECURE_SSL_REDIRECT=false\n")
        f.write("export USE_S3=True\n")
        f.write("\n")
        f.write("# Start the server\n")
        f.write(f"exec gunicorn -c {output_file} main:app\n")
    
    os.chmod(wrapper_script, 0o755)  # Make executable
    
    logger.info(f"Wrapper script created: {wrapper_script}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())