#!/usr/bin/env python3
"""
HTTP-only runner for Django that works in Replit environment
Avoids SSL certificate issues and creates missing database tables
"""
import os
import sys
import django
from django.db import connection

# Configure environment for HTTP mode
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"

# Set up Django
django.setup()

# Update Django settings
from django.conf import settings
settings.CSRF_COOKIE_SECURE = False
settings.SESSION_COOKIE_SECURE = False
settings.CORS_ALLOW_CREDENTIALS = True
settings.CORS_ALLOW_ALL_ORIGINS = True
settings.CSRF_TRUSTED_ORIGINS = [
    f'http://{os.environ.get("REPLIT_DOMAIN", "*")}',
    f'https://{os.environ.get("REPLIT_DOMAIN", "*")}'
]

# Fix missing karma table issue
def create_karma_table_if_missing():
    """Create the karma event table if it doesn't exist"""
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = 'critique_karmaevent'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("Creating KarmaEvent table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS critique_karmaevent (
                    id SERIAL PRIMARY KEY,
                    points INTEGER NOT NULL,
                    reason VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                    content_type_id INTEGER REFERENCES django_content_type(id) ON DELETE CASCADE,
                    object_id INTEGER
                )
            """)
            print("KarmaEvent table created successfully!")
        else:
            print("KarmaEvent table already exists")

# Run table creation before starting server
create_karma_table_if_missing()

# Now run the Django server
if __name__ == "__main__":
    print("Starting pure HTTP Django server on port 5000...")
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])