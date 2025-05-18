#!/bin/bash
# HTTP-only startup script for Brush Up application
# This script runs the Django server directly without requiring SSL certificates

echo "-----------------------------------------------------"
echo "Starting Brush Up application in HTTP mode..."
echo "-----------------------------------------------------"

# First, fix the CritiqueSerializer to ensure it has the get_reactions_count method
echo "Fixing CritiqueSerializer..."
python fix_critique_serializer.py

# Check if the KarmaEvent table exists
echo "Verifying database tables..."
python fix_karma_db.py

# Start the Django server in HTTP mode
echo "-----------------------------------------------------"
echo "Starting HTTP server on port 5000"
echo "-----------------------------------------------------"
exec python server.py