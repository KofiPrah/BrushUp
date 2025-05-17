#!/usr/bin/env python3
"""
A simple HTTP server for Art Critique (without SSL)
"""
from flask import Flask, redirect

# Create a simple Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Redirect to the Django app"""
    return redirect('/critique/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Run with HTTP (not HTTPS)
    print("Starting HTTP server on port 8000...")
    app.run(host='0.0.0.0', port=8000)