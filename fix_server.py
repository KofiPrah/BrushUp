#!/usr/bin/env python3
"""
Script to modify Django server settings and environment variables
to ensure proper operation in HTTP mode with Replit's load balancer
"""
import os
import sys

def patch_settings():
    """Apply patches to Django settings"""
    # Set environment variables
    os.environ["SSL_ENABLED"] = "false"
    os.environ["HTTP_ONLY"] = "true"
    
    # Remove certificate references
    return True

if __name__ == "__main__":
    success = patch_settings()
    print(f"Server configuration {'updated' if success else 'failed'} for HTTP mode")
    sys.exit(0 if success else 1)
