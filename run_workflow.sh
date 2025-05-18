#!/bin/bash
# Workflow script for Brush Up application in HTTP mode
exec gunicorn --bind 0.0.0.0:5000 --reload main:app