#!/usr/bin/env python
"""
A simple HTTP-only media server for Art Critique.

This server handles media file requests without requiring SSL, making it compatible
with Replit's load balancer. It should be run alongside the main Django application.
"""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('media_server')

# Configuration
PORT = 8080  # Different port from main app
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')

class MediaFileHandler(SimpleHTTPRequestHandler):
    """Custom handler that serves files from the media directory."""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        self.directory = MEDIA_ROOT
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override log_message to use our logger."""
        logger.info("%s - %s", self.address_string(), format % args)
    
    def end_headers(self):
        """Add CORS headers to allow cross-origin requests."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        return super().end_headers()

def main():
    """Start the media file server."""
    logger.info(f"Starting media file server on port {PORT}")
    logger.info(f"Serving files from: {MEDIA_ROOT}")
    
    # Create the directory if it doesn't exist
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    
    # List files in the media directory
    logger.info("Files in media directory:")
    for root, dirs, files in os.walk(MEDIA_ROOT):
        for file in files:
            logger.info(f"  {os.path.join(root, file)}")
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), MediaFileHandler)
        logger.info(f"Server started at http://0.0.0.0:{PORT}")
        logger.info(f"Use Ctrl+C to stop")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped.")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()