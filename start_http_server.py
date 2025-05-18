#!/usr/bin/env python
"""
HTTP-only server starter for Brush Up application

This script runs the Django application in HTTP-only mode,
bypassing SSL certificate requirements that cause issues in Replit.
"""
import os
import sys
import subprocess

def print_banner(message):
    """Print a styled banner message"""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "*"))
    print("=" * 80 + "\n")

def fix_critique_serializer():
    """Add missing get_reactions_count method to CritiqueSerializer if needed"""
    from critique.api.serializers import CritiqueSerializer
    
    # Check if the method already exists
    if hasattr(CritiqueSerializer, 'get_reactions_count'):
        print("✓ CritiqueSerializer already has get_reactions_count method")
        return
    
    # Add the missing method
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return obj.reactions.count()
    
    # Add the method to the class
    setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
    print("✓ Added missing get_reactions_count method to CritiqueSerializer")

def check_database_tables():
    """Check if necessary database tables exist and create them if needed"""
    import django
    from django.db import connection
    
    # Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
    django.setup()
    
    def check_table_exists(table_name):
        """Check if a table exists in the database"""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_name = %s
                );
                """, 
                [table_name]
            )
            return cursor.fetchone()[0]
    
    # Check for required tables
    required_tables = [
        'critique_karmaevent',
        'critique_reaction',
        'critique_critique'
    ]
    
    missing_tables = []
    for table in required_tables:
        if not check_table_exists(table):
            missing_tables.append(table)
    
    if missing_tables:
        print(f"! Missing tables: {', '.join(missing_tables)}")
        print("Running Django migrations to create missing tables...")
        from django.core.management import call_command
        call_command('migrate')
        print("✓ Migrations completed")
    else:
        print("✓ All required database tables exist")

def start_http_server():
    """Start the Django application with gunicorn in HTTP mode"""
    print_banner("Starting Brush Up in HTTP Mode")
    
    # Fix the serializer if needed
    try:
        fix_critique_serializer()
    except Exception as e:
        print(f"! Error fixing serializer: {e}")
    
    # Check database tables
    try:
        check_database_tables()
    except Exception as e:
        print(f"! Error checking database tables: {e}")
    
    # Start the Django application with gunicorn
    print_banner("Starting Django with Gunicorn (HTTP Mode)")
    gunicorn_command = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reuse-port",
        "--reload",
        "artcritique.wsgi:application"
    ]
    
    try:
        subprocess.run(gunicorn_command)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_http_server()