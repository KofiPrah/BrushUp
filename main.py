#!/usr/bin/env python3
"""
Main entry point for Brush Up application
Works with both HTTP and HTTPS modes
"""
import os
import sys
from flask import Flask, redirect

# Create a simple Flask app that will be used by gunicorn
app = Flask(__name__)

@app.route('/')
def index():
    """Redirect to the Django app"""
    return redirect('/critique/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK'

# Set Django settings module
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

if __name__ == "__main__":
    print("Starting Brush Up application...")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)