#!/usr/bin/env python3
"""
HTTP-only main file for workflow use

This script runs the HTTP-only version of the Brush Up application
without requiring SSL certificates.
"""
import os
import subprocess
import sys

# Run our HTTP-only startup script
subprocess.run(["./run.sh"])