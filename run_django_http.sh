#!/bin/bash

# Force HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true

# Start Django server
python manage.py runserver 0.0.0.0:5000