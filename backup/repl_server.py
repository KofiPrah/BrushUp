#!/usr/bin/env python3
"""
HTTP server for Brush Up application in Replit
"""
import os
import sys

# Set environment for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Fix database tables if needed
print("Checking database tables...")
try:
    import psycopg2
    import os
    
    # Get database connection details from environment
    db_url = os.environ.get('DATABASE_URL')
    
    # Create KarmaEvent table if it doesn't exist
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_name = 'critique_karmaevent'
                );
            """)
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                print("Creating KarmaEvent table...")
                cur.execute("""
                    CREATE TABLE critique_karmaevent (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        event_type VARCHAR(50) NOT NULL,
                        points INTEGER NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
                    );
                """)
                conn.commit()
                print("Created KarmaEvent table")
            else:
                print("KarmaEvent table already exists")
    
    print("Database setup complete")
except Exception as e:
    print(f"Database check error: {str(e)}")

# Now import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Make it accessible as 'app' for gunicorn
app = application