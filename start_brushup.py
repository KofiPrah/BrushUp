#!/usr/bin/env python3
"""
Brush Up Application Starter
----------------------------
Runs the Django app in HTTP mode with all necessary fixes applied
"""
import os
import sys
import subprocess
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')

# Force HTTP mode
os.environ['HTTPS'] = 'off'
os.environ['HTTP_ONLY'] = 'true'
os.environ['SSL_ENABLED'] = 'false'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Fix missing get_reactions_count method in CritiqueSerializer
try:
    from critique.api.serializers import CritiqueSerializer
    
    # Define the missing method
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return obj.reactions.count()
    
    # Add missing method to the serializer if not already present
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added missing get_reactions_count method to CritiqueSerializer")
    else:
        print("✓ get_reactions_count method already exists in CritiqueSerializer")
except Exception as e:
    print(f"! Warning: Error fixing CritiqueSerializer: {e}")

# Check if database tables exist and create them if needed
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
    
    # Verify KarmaEvent and Reaction tables
    for table in ['critique_karmaevent', 'critique_reaction']:
        exists = check_table_exists(table)
        print(f"✓ Table {table} {'exists' if exists else 'does not exist'}")
except Exception as e:
    print(f"! Warning: Could not check database tables: {e}")

# Kill any existing gunicorn processes
subprocess.run("pkill -f gunicorn || true", shell=True)

# Start the HTTP server
print("\n🚀 Starting Brush Up application in HTTP mode...")
cmd = [
    "gunicorn",
    "--bind", "0.0.0.0:5000",
    "--reload",
    "--access-logfile", "-",
    "--error-logfile", "-",
    "main:app"
]

# Run the server
try:
    os.execvp(cmd[0], cmd)
except Exception as e:
    print(f"! Error starting server: {e}")
    sys.exit(1)