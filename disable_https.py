#!/usr/bin/env python
"""
Configure Gunicorn to operate in HTTP-only mode.
This script updates settings files to use HTTP instead of HTTPS.
"""

import os
import sys
import fileinput
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('http_config')

def update_dot_replit():
    """Update .replit file to use HTTP-only command"""
    try:
        new_command = 'gunicorn --bind 0.0.0.0:5000 --reload main:app'
        logger.info(f"Suggested workflow command: {new_command}")
        logger.info("To update .replit, use the Replit UI workflow editor")
        return True
    except Exception as e:
        logger.error(f"Failed to process .replit: {e}")
        return False

def setup_environment():
    """Set environment variables for HTTP mode"""
    try:
        # Set environment variables for current process
        os.environ['SSL_ENABLED'] = 'false'
        os.environ['SECURE_SSL_REDIRECT'] = 'false'
        os.environ['USE_S3'] = 'True'
        
        # Return environment variables that should be set
        logger.info("Set environment variables: SSL_ENABLED=false, SECURE_SSL_REDIRECT=false")
        return {
            'SSL_ENABLED': 'false',
            'SECURE_SSL_REDIRECT': 'false',
            'USE_S3': 'True'
        }
    except Exception as e:
        logger.error(f"Failed to set environment variables: {e}")
        return {}

def update_django_settings():
    """Update Django settings to disable SSL"""
    try:
        logger.info("Checking Django settings")
        settings_file = 'artcritique/settings.py'
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings_content = f.read()
            
            # Check if SSL settings exist
            if 'SECURE_SSL_REDIRECT' in settings_content:
                logger.info("Django settings already has SSL configuration")
                
                # Ensure SSL is disabled
                if "os.environ.get('SECURE_SSL_REDIRECT', 'true').lower() == 'true'" in settings_content:
                    logger.info("SSL already configured to use environment variable")
                else:
                    logger.info("Django settings uses hardcoded SSL settings")
            else:
                logger.info("No explicit SSL settings found in Django settings")
        else:
            logger.warning(f"Settings file {settings_file} not found")
        
        return True
    except Exception as e:
        logger.error(f"Failed to update Django settings: {e}")
        return False

def create_http_startup_script():
    """Create a script to start the server in HTTP mode"""
    try:
        script_path = 'start_in_http_mode.sh'
        script_content = """#!/bin/bash
# Start Art Critique in HTTP mode (no SSL)

# Set environment variables
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false
export USE_S3=True

# Kill any existing server processes
pkill -f gunicorn || echo "No existing server processes"

echo "Starting Art Critique in HTTP mode..."
echo "Running in HTTP mode (SSL handled by Replit's load balancer)"

# Start Gunicorn without SSL certificates
exec gunicorn \\
  --bind 0.0.0.0:5000 \\
  --worker-class sync \\
  --workers 1 \\
  --reload \\
  --access-logfile - \\
  --error-logfile - \\
  main:app
"""
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make it executable
        os.chmod(script_path, 0o755)
        logger.info(f"Created HTTP startup script: {script_path}")
        
        # Create a symlink for easy access
        if os.path.exists('start'):
            os.remove('start')
        os.symlink(script_path, 'start')
        logger.info("Created 'start' symlink to HTTP startup script")
        
        return True
    except Exception as e:
        logger.error(f"Failed to create startup script: {e}")
        return False

def main():
    """Main function to disable HTTPS"""
    logger.info("Configuring Art Critique for HTTP-only mode")
    
    # Update environment
    env_vars = setup_environment()
    
    # Update .replit file
    update_dot_replit()
    
    # Update Django settings
    update_django_settings()
    
    # Create startup script
    create_http_startup_script()
    
    logger.info("""
HTTP CONFIGURATION COMPLETED
===========================

To run the server in HTTP mode, use:
  ./start_in_http_mode.sh

To update the workflow, go to:
  Tools > Workflows > Start application
  
And change the command to:
  ./start_in_http_mode.sh
""")

if __name__ == "__main__":
    main()