"""
Simple script to run the Django application over HTTP (no SSL).
This is useful for testing when SSL issues occur.
"""

import os
import sys
from django.core.management import execute_from_command_line

def main():
    """Run development server without SSL"""
    print("Running Django server over HTTP (no SSL)")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
    # Add HTTP settings
    os.environ["DJANGO_INSECURE"] = "1"  # Allow insecure connections for testing
    # Run the development server
    sys.argv = ["manage.py", "runserver", "0.0.0.0:8000"]
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()