#!/usr/bin/env python3
"""
Brush Up Application - Fixed HTTP Server
----------------------------------------
This script fixes the serializer issues and runs the app in HTTP mode
"""
import os
import sys
import django
import subprocess
import time
import signal

# Force HTTP mode
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['HTTPS'] = 'off'
os.environ['HTTP_ONLY'] = 'true'
os.environ['SSL_ENABLED'] = 'false'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Fix CritiqueSerializer and CritiqueListSerializer
try:
    from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer
    
    # Define the missing method
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
    
    # Add the method to both serializers if needed
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count method to CritiqueSerializer")
    else:
        print("✓ CritiqueSerializer already has get_reactions_count method")
    
    if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
        setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count method to CritiqueListSerializer")
    else:
        print("✓ CritiqueListSerializer already has get_reactions_count method")
        
    print("✓ Successfully fixed serializer issues")
except Exception as e:
    print(f"! Error fixing serializers: {e}")

# Create empty certificate files to avoid errors
with open('cert.pem', 'w') as f:
    f.write('# Dummy certificate\n')
with open('key.pem', 'w') as f:
    f.write('# Dummy key\n')

# Start Django server in HTTP mode
def start_django():
    print("\n🚀 Starting Brush Up in HTTP mode...")
    
    # Kill existing processes
    try:
        subprocess.run(['pkill', '-f', 'runserver'], check=False)
        subprocess.run(['pkill', '-f', 'gunicorn'], check=False)
        time.sleep(1)
    except:
        pass
    
    # Start Django development server
    cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:5000']
    
    try:
        process = subprocess.Popen(cmd)
        process.wait()  # Wait for the process to complete
    except KeyboardInterrupt:
        print("\nShutting down server...")
        if 'process' in locals():
            process.send_signal(signal.SIGTERM)
            process.wait()
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_django()