#!/usr/bin/env python3
"""
Script to fix the server configuration for Brush Up application
Removes SSL certificates and updates main.py for HTTP mode
"""
import os
import shutil
from pathlib import Path

def remove_ssl_certificates():
    """Rename SSL certificates to disable them"""
    print("Removing SSL certificates...")
    
    cert_path = Path("cert.pem")
    key_path = Path("key.pem")
    
    if cert_path.exists():
        backup_path = Path("cert.pem.bak")
        if not backup_path.exists():
            shutil.copy(cert_path, backup_path)
        cert_path.unlink(missing_ok=True)
        print(f"Renamed {cert_path} to {backup_path}")
    
    if key_path.exists():
        backup_path = Path("key.pem.bak")
        if not backup_path.exists():
            shutil.copy(key_path, backup_path)
        key_path.unlink(missing_ok=True)
        print(f"Renamed {key_path} to {backup_path}")

def update_main_py():
    """Update main.py to use HTTP mode"""
    print("Updating main.py for HTTP mode...")
    
    with open("main.py", "w") as f:
        f.write("""#!/usr/bin/env python3
'''
Simple HTTP-only Django app for Brush Up in Replit environment
'''
import os

# Configure Django for HTTP mode
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Create app variable for gunicorn
app = application
""")

def create_fix_karma_script():
    """Create a script to fix the KarmaEvent database table if missing"""
    print("Creating fix_karma_db.py script...")
    
    with open("fix_karma_db.py", "w") as f:
        f.write('''#!/usr/bin/env python3
"""
Script to ensure the KarmaEvent table exists in the database
"""
import os
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
django.setup()

import psycopg2
from django.conf import settings
from django.db import connection

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)",
            [table_name]
        )
        return cursor.fetchone()[0]

def create_karma_tables():
    """Create the KarmaEvent tables if they don't exist"""''')
    karma_table_exists = check_table_exists('critique_karmaevent')
    
    if not karma_table_exists:
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

if __name__ == "__main__":
    print("Checking and fixing database tables...")
    create_karma_tables()
    print("Database check complete.")
""")

def main():
    """Run all fix operations"""
    remove_ssl_certificates()
    update_main_py()
    create_fix_karma_script()
    
    print("\nAll fixes applied successfully!")
    print("1. SSL certificates have been disabled")
    print("2. main.py has been updated for HTTP mode")
    print("3. A script to fix the KarmaEvent table has been created")
    print("\nYou can now run the server in HTTP mode with:")
    print("   gunicorn --bind 0.0.0.0:5000 main:app")
    print("\nTo fix the KarmaEvent table if needed, run:")
    print("   python fix_karma_db.py")

if __name__ == "__main__":
    main()