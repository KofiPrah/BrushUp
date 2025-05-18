#!/usr/bin/env python3
"""
Brush Up Application Launcher
----------------------------
HTTP-only server with CritiqueSerializer fixes
"""
import os
import sys
import subprocess
import signal
import time

# Configure environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'
os.environ['PYTHONUNBUFFERED'] = '1'

# Initialize Django
import django
django.setup()

# Fix serializer issues
try:
    from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer
    
    has_method = hasattr(CritiqueSerializer, 'get_reactions_count')
    if not has_method:
        print("Adding missing get_reactions_count method to serializers...")
        
        # Define missing method
        def get_reactions_count(self, obj):
            """Return the total count of all reactions for this critique."""
            return {
                'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
                'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
                'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
                'TOTAL': obj.reactions.count()
            }
        
        # Add method to both serializers
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
        
        print("✓ Added get_reactions_count method to serializers")
    else:
        print("✓ get_reactions_count method already exists in serializers")
except Exception as e:
    print(f"! Error fixing serializers: {e}")

print("\n🚀 Starting Brush Up application in HTTP mode...")
print("This server runs Django directly, without gunicorn or SSL")
print("The site will be available at: http://<your-replit-url>")

# Kill any existing servers
try:
    subprocess.run(['pkill', '-f', 'runserver'], check=False)
    subprocess.run(['pkill', '-f', 'gunicorn'], check=False)
    time.sleep(1)
except:
    pass

# Create dummy certificate files to prevent errors
with open('cert.pem', 'w') as f:
    f.write('# Dummy certificate\n')
with open('key.pem', 'w') as f:
    f.write('# Dummy key\n')

# Launch Django's built-in development server
command = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:5000']

try:
    process = subprocess.Popen(command)
    process.wait()  # Wait for the process to complete
except KeyboardInterrupt:
    print("\nShutting down server...")
    process.send_signal(signal.SIGTERM)
    process.wait()
except Exception as e:
    print(f"Error running server: {e}")
    sys.exit(1)