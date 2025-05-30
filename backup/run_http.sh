#!/bin/bash
# HTTP-only server for Brush Up application

# Apply the fix for CritiqueSerializer first
python -c "from fix_critique_serializer import add_missing_method; add_missing_method(); print('✓ Fixed CritiqueSerializer successfully')"

# Run Django directly using gunicorn without SSL certificates
echo "Starting Brush Up in HTTP mode (no SSL)..."
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app