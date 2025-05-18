#!/bin/bash
# Start server without SSL certificates
python3 -c "import sys; open(\"cert.pem\", \"w\").close(); open(\"key.pem\", \"w\").close();"
exec gunicorn --bind 0.0.0.0:5000 main:app

