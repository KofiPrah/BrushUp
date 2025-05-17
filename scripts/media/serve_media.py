#!/usr/bin/env python
"""
A simple HTTP server specifically for serving media files.
This is needed to work around SSL issues with Replit.
"""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Configuration
PORT = 8000
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
RESTRICTED_PATHS = ['/admin', '/api', '/accounts']  # Restrict access to these paths

class MediaFileHandler(SimpleHTTPRequestHandler):
    """Custom handler that only serves files from the media directory."""
    
    def translate_path(self, path):
        """Translate path to serve files from the media directory."""
        # Remove query parameters if any
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        
        # Check if path starts with /media/
        if path.startswith('/media/'):
            # Strip /media/ and join with MEDIA_ROOT
            rel_path = path[7:]  # Remove /media/ prefix
            return os.path.join(MEDIA_ROOT, rel_path)
        
        # For any other path, return a 404
        return ""
    
    def do_GET(self):
        """Handle GET requests."""
        # Only serve media files
        if not self.path.startswith('/media/'):
            self.send_error(404, "File not found")
            return
            
        # Check for restricted paths
        for restricted in RESTRICTED_PATHS:
            if restricted in self.path:
                self.send_error(403, "Forbidden")
                return
                
        return SimpleHTTPRequestHandler.do_GET(self)

def main():
    """Start the media file server."""
    print(f"Starting media file server on port {PORT}")
    print(f"Serving files from: {MEDIA_ROOT}")
    
    # Create the directory if it doesn't exist
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), MediaFileHandler)
        print(f"Server started at http://0.0.0.0:{PORT}")
        print(f"Use Ctrl+C to stop")
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()