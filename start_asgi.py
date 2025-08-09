#!/usr/bin/env python3
"""
ASGI server startup script for Django Channels support.
This script starts an ASGI server (Daphne) to support both HTTP and WebSocket connections.
"""

import os
import sys
import django
from channels.routing import get_default_application

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')

# Setup Django
django.setup()

def main():
    """Start the ASGI application server."""
    import logging
    from daphne.server import Server
    from daphne.endpoints import build_endpoint_description_strings
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Enable ASGI application
    from django.conf import settings
    settings.ASGI_APPLICATION = 'artcritique.asgi.application'
    
    # Import the application
    from artcritique.asgi import application
    
    # Server configuration
    host = '0.0.0.0'
    port = 5000
    
    logger.info(f"Starting ASGI server on {host}:{port}")
    logger.info("WebSocket support enabled for real-time notifications")
    
    # Create and start server
    try:
        server = Server(
            application,
            endpoints=build_endpoint_description_strings(host=host, port=port),
            verbosity=1,
        )
        
        logger.info("ASGI server started successfully")
        logger.info("Both HTTP and WebSocket protocols supported")
        
        server.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()