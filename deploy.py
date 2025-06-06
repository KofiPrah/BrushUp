#!/usr/bin/env python3
"""
Deployment script for Brush Up on Replit Autoscale
This script ensures the application is properly configured for production deployment
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_deployment_server():
    """Run the application with production-ready Gunicorn configuration"""
    
    # Set production environment variables
    env_vars = {
        'DJANGO_SETTINGS_MODULE': 'artcritique.settings',
        'SSL_ENABLED': 'false',
        'HTTP_ONLY': 'true',
        'PORT': os.environ.get('PORT', '8080'),
        'PYTHONUNBUFFERED': '1',
    }
    
    # Update environment
    os.environ.update(env_vars)
    
    # Construct gunicorn command for deployment
    cmd = [
        'gunicorn',
        '--config', 'gunicorn.conf.py',
        'main:app'
    ]
    
    logger.info(f"Starting deployment server on port {env_vars['PORT']}")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        # Run the server
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Deployment server failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Deployment server stopped")
        sys.exit(0)

def verify_deployment():
    """Verify the deployment is working correctly"""
    import requests
    import time
    
    port = os.environ.get('PORT', '8080')
    health_url = f"http://localhost:{port}/health/"
    
    logger.info("Verifying deployment health...")
    
    # Wait a moment for server to start
    time.sleep(2)
    
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Health check passed: {data}")
            return True
        else:
            logger.error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return False

if __name__ == '__main__':
    logger.info("Starting Brush Up deployment")
    
    # For verification mode
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        success = verify_deployment()
        sys.exit(0 if success else 1)
    
    # Run deployment server
    run_deployment_server()