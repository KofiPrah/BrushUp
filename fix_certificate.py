#!/usr/bin/env python3
"""
This script removes or modifies the SSL certificates to enable HTTP mode
"""
import os
import shutil

# Backup original certificates if they exist
if os.path.exists('cert.pem'):
    if not os.path.exists('cert.pem.bak'):
        shutil.copy('cert.pem', 'cert.pem.bak')
    os.remove('cert.pem')

if os.path.exists('key.pem'):
    if not os.path.exists('key.pem.bak'):
        shutil.copy('key.pem', 'key.pem.bak')
    os.remove('key.pem')

# Create empty certificate files
with open('cert.pem', 'w') as f:
    f.write('# Certificate disabled for HTTP mode\n')

with open('key.pem', 'w') as f:
    f.write('# Key disabled for HTTP mode\n')

print("Certificates modified to enable HTTP mode")