#!/usr/bin/env python3
"""
Fix database issues with KarmaEvent table
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
django.setup()

# Import Django models and db utilities
from django.db import connection
from django.core.management import call_command

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE  table_schema = 'public'
                AND    table_name   = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def create_karma_tables():
    """Create the KarmaEvent tables if they don't exist"""
    # First check if the table exists
    if not check_table_exists('critique_karmaevent'):
        print("Creating KarmaEvent table...")
        
        # Create the table using raw SQL
        with connection.cursor() as cursor:
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
        print("KarmaEvent table created successfully")
    else:
        print("KarmaEvent table already exists")

if __name__ == "__main__":
    create_karma_tables()
    print("Database fixes applied successfully")