"""
Direct HTTP server for Brush Up application
This script runs Django directly without SSL requirements
"""
import os
import sys
import signal
import django
from django.core.management import execute_from_command_line

# Handle termination signals
def signal_handler(sig, frame):
    print("\nShutting down server...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DJANGO_DEBUG'] = 'true'
    
    # Print banner
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP SERVER ".center(70, '='))
    print("=" * 70)
    print("Starting Django development server on port 5000")
    
    # Initialize Django
    django.setup()
    
    # Run Django development server
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()