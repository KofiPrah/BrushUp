#!/usr/bin/env python
"""
Entry point for running the Flask application in HTTP mode.
This script ensures the correct settings are applied before starting.
"""

# Import the HTTP-only settings first to apply them
import http_only_settings

# Then import the Flask app
from main import app

if __name__ == "__main__":
    print("Starting Flask application in HTTP mode...")
    # Run with Flask's development server
    app.run(host="0.0.0.0", port=5000, debug=True)