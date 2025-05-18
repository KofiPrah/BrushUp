"""
HTTP-only server for Art Critique

This script runs a pure HTTP server for the Art Critique app
without using SSL certificates, compatible with Replit's load balancer.
"""

import os
from flask import Flask, redirect
from artcritique.wsgi import application as django_app

# Force HTTP mode for compatibility with Replit's load balancer
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# For WSGI application
app = django_app

if __name__ == "__main__":
    # Print startup information
    print("Using HTTP mode (SSL handled by Replit's load balancer)")
    
    # Create a simple Flask app for direct running
    flask_app = Flask(__name__)
    
    @flask_app.route('/')
    def index():
        """Redirect to the Django app"""
        return redirect('/critique/')
    
    @flask_app.route('/health')
    def health():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    # Run the Flask app
    flask_app.run(host='0.0.0.0', port=5000)