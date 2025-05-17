"""
A Simple WSGI HTTP server for Django using Gunicorn without SSL.
"""
import os
import sys
from gunicorn.app.wsgiapp import WSGIApplication

# Make sure Django knows where to find settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Ensure mathfilters is available
try:
    import mathfilters
    print("mathfilters module is available")
except ImportError:
    print("Warning: mathfilters module not found")

if __name__ == '__main__':
    # Setup the command line arguments
    sys.argv = [
        'gunicorn',
        '--bind=0.0.0.0:5000',
        '--workers=1',
        'artcritique.wsgi:application'
    ]
    
    print("Starting Gunicorn without SSL...")
    WSGIApplication().run()