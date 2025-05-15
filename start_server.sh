#!/bin/bash
# Start the server in plain HTTP mode
# Use $PORT environment variable which is provided by Replit
PORT="${PORT:-5000}"
gunicorn --bind "0.0.0.0:$PORT" --reuse-port --reload main:app