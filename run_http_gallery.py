#!/usr/bin/env python3
"""
HTTP-only server for testing the enhanced Gallery with pagination
Bypasses SSL configuration issues
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
    django.setup()
    
    # Run Django development server on HTTP only
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:5000'])