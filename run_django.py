"""
Direct Django server runner
Bypasses SSL certificate issues by directly using Django's runserver
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Run Django directly using runserver"""
    
    # Set environment variables
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Print startup message
    print("=" * 80)
    print("Starting Django development server on port 5000")
    print("=" * 80)
    
    # Set up and run Django
    django.setup()
    
    # Run Django's development server
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()