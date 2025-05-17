"""
Simple HTTP server for Art Critique

This script runs a pure HTTP server for the Art Critique app
without using SSL certificates.
"""

import os
from flask import Flask, redirect

# Create a minimal Flask app for HTTP mode
app = Flask(__name__)

@app.route('/')
def http_index():
    """Redirect to the main application"""
    return "HTTP Server is running. Visit the application at the standard URL."

if __name__ == '__main__':
    # Force HTTP mode
    os.environ['SSL_ENABLED'] = 'false'
    os.environ['HTTP_ONLY'] = 'true'
    
    print("Starting HTTP-only server...")
    app.run(host='0.0.0.0', port=5000)