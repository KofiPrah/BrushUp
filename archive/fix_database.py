#!/usr/bin/env python3
"""
Script to verify and fix database tables for Brush Up application
"""
import os
import django

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Now we can import Django models
from django.db import connection, transaction
from django.contrib.auth.models import User
from critique.models import KarmaEvent, Reaction, Critique

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)",
            [table_name]
        )
        return cursor.fetchone()[0]

def create_karma_event_table():
    """Create the KarmaEvent table if it doesn't exist"""
    table_exists = check_table_exists('critique_karmaevent')
    
    if not table_exists:
        print("KarmaEvent table doesn't exist. Creating it...")
        with connection.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS critique_karmaevent (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES auth_user(id),
                event_type VARCHAR(50) NOT NULL,
                points INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                reference_id INTEGER,
                reference_type VARCHAR(50)
            );
            ''')
        print("KarmaEvent table created successfully.")
    else:
        print("KarmaEvent table already exists.")

def create_reaction_table():
    """Create the Reaction table if it doesn't exist"""
    table_exists = check_table_exists('critique_reaction')
    
    if not table_exists:
        print("Reaction table doesn't exist. Creating it...")
        with connection.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS critique_reaction (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES auth_user(id),
                critique_id INTEGER NOT NULL REFERENCES critique_critique(id),
                reaction_type VARCHAR(20) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id, critique_id, reaction_type)
            );
            ''')
        print("Reaction table created successfully.")
    else:
        print("Reaction table already exists.")

def check_migrations():
    """Check if migrations table exists and is properly configured"""
    migrations_exist = check_table_exists('django_migrations')
    
    if not migrations_exist:
        print("Django migrations table doesn't exist. This might cause issues.")
        print("Consider running 'python manage.py migrate' to set up all tables.")
    else:
        print("Django migrations table exists.")

def main():
    """Run all database checks and fixes"""
    print("Checking database tables...")
    check_migrations()
    create_karma_event_table()
    create_reaction_table()
    print("All database checks completed.")
    
if __name__ == "__main__":
    main()