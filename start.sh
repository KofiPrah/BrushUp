#!/bin/bash
# Script to start the server with the right configuration

# Start the server in HTTP mode
gunicorn --bind 0.0.0.0:5000 --reload main:app