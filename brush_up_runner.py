#!/usr/bin/env python3
"""
Brush Up Application Runner
-------------------------
Fixed HTTP server with correct serializers
"""
import os
import sys
import django
import subprocess
import time
import signal

# Kill any existing servers
try:
    subprocess.run(["pkill", "-f", "gunicorn"], check=False)
    subprocess.run(["pkill", "-f", "runserver"], check=False)
    time.sleep(1)
except:
    pass

# Create empty certificate files
with open("cert.pem", "w") as f:
    f.write("# Empty certificate file\n")
with open("key.pem", "w") as f:
    f.write("# Empty key file\n")

# Set environment variables for HTTP mode
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTPS'] = 'off'
os.environ['HTTP_ONLY'] = 'true'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Fix serializer issues
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
    
    # Add method to both serializers if needed
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count method to CritiqueSerializer")
    
    if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
        setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count method to CritiqueListSerializer")
    
    print("✓ CritiqueSerializer fixes completed successfully")
except Exception as e:
    print(f"! Error fixing serializers: {e}")

# Check that critical database tables exist
try:
    from django.db import connection
    
    def check_table_exists(table_name):
        """Check if a table exists in the database"""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)",
                [table_name]
            )
            return cursor.fetchone()[0]
    
    # Check KarmaEvent and Reaction tables
    karma_exists = check_table_exists('critique_karmaevent')
    reaction_exists = check_table_exists('critique_reaction')
    
    print(f"✓ Table critique_karmaevent {'exists' if karma_exists else 'does not exist'}")
    print(f"✓ Table critique_reaction {'exists' if reaction_exists else 'does not exist'}")
    
    # Create tables if needed
    if not karma_exists or not reaction_exists:
        print("! Running migrations to create missing tables...")
        from django.core.management import execute_from_command_line
        execute_from_command_line(["manage.py", "migrate"])
except Exception as e:
    print(f"! Error checking database tables: {e}")

# Start the server (Django development server for simplicity and reliability)
print("\n🚀 Starting Brush Up in HTTP mode (without SSL certificates)...")
cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:5000"]

try:
    process = subprocess.Popen(cmd)
    process.wait()
except KeyboardInterrupt:
    if 'process' in locals():
        process.send_signal(signal.SIGTERM)
        process.wait()
except Exception as e:
    print(f"! Error starting server: {e}")
    sys.exit(1)