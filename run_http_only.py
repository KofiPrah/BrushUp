"""
Simple HTTP-only server for Brush Up application
Runs without SSL certificates to avoid common Replit issues
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Run Django in HTTP-only mode without SSL"""
    # Set Django environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DEBUG'] = 'true'
    
    # Rename SSL certificates to disable them
    for cert_file in ['cert.pem', 'key.pem']:
        if os.path.exists(cert_file):
            if not os.path.exists(f"{cert_file}.disabled"):
                os.rename(cert_file, f"{cert_file}.disabled")
                print(f"Renamed {cert_file} to {cert_file}.disabled to disable SSL")
    
    # Create empty certificate files (to avoid errors in other scripts)
    with open('cert.pem', 'w') as f:
        pass
    with open('key.pem', 'w') as f:
        pass
    
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP ONLY SERVER ".center(70, '='))
    print("=" * 70)
    print("Starting Django development server on port 5000")
    
    # Initialize Django
    django.setup()
    
    # Run the Django development server
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()