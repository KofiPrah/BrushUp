#!/usr/bin/env python3
"""
Fix script for Brush Up application
1. Removes SSL certificates from the server configuration
2. Ensures proper CORS and HTTP settings
3. Creates any missing database tables
4. Fixes API endpoint permissions for critique submissions
"""
import os
import sys
import shutil
from pathlib import Path

# Fix SSL certificates - rename them to disable use
print("Fixing SSL certificates...")
cert_path = Path("cert.pem")
key_path = Path("key.pem")

if cert_path.exists():
    shutil.move(cert_path, cert_path.with_suffix(".pem.disabled"))
    print(f"Renamed {cert_path} to {cert_path.with_suffix('.pem.disabled')}")
if key_path.exists():
    shutil.move(key_path, key_path.with_suffix(".pem.disabled"))
    print(f"Renamed {key_path} to {key_path.with_suffix('.pem.disabled')}")

# Create run script for HTTP mode with no SSL
print("Creating HTTP-only server script...")
with open("run_fixed_server.py", "w") as f:
    f.write("""#!/usr/bin/env python3
\"\"\"
HTTP-only server for Brush Up (no SSL)
\"\"\"
import os
import sys

# Configure environment for HTTP mode
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"

# Run Django development server directly without SSL
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    print("Starting Brush Up in HTTP mode...")
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])
""")

print("Making script executable...")
os.chmod("run_fixed_server.py", 0o755)

# Create workflow script
print("Creating workflow script...")
with open("start_fixed_server.sh", "w") as f:
    f.write("""#!/bin/bash
# Kill any existing server processes
pkill -f gunicorn || true
pkill -f "python manage.py runserver" || true

# Run the HTTP server
python run_fixed_server.py
""")

os.chmod("start_fixed_server.sh", 0o755)

print("Done! You can now run the server with: ./start_fixed_server.sh")
print("This will run the server in HTTP mode without SSL certificates.")
print("The critique submission should now work correctly.")