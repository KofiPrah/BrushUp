#!/bin/bash
# Simple HTTP-only startup script for Brush Up application

echo "Starting Brush Up application in HTTP mode..."

# Fix the missing method in CritiqueSerializer
python fix_critique_serializer.py

# Check if KarmaEvent table exists
python fix_karma_db.py

# Start Django directly instead of using gunicorn with SSL
echo "Starting Django server on port 5000..."
exec python server.py