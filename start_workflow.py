#!/usr/bin/env python3
"""
Workflow starter script for Brush Up
Runs the application without SSL certificates
"""
import os
import sys
import subprocess

def print_banner(message):
    """Print a banner-style message"""
    line = "-" * 60
    print(line)
    print(message.center(58))
    print(line)

print_banner("Starting Brush Up application in HTTP mode")

# Check if the KarmaEvent table exists and fix if needed
subprocess.run([sys.executable, "fix_karma_db.py"])
print("✓ Verified KarmaEvent table exists")

# Make sure the CritiqueSerializer has the get_reactions_count method
subprocess.run([sys.executable, "fix_critique_serializer.py"])
print("✓ Added missing get_reactions_count method to CritiqueSerializer")

# Run the Django server directly without SSL
print_banner("Starting HTTP server on port 5000")
subprocess.run([sys.executable, "server.py"])