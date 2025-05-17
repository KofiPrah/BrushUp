#!/usr/bin/env python3
"""
Test script for HTTP workflow configuration.
This script tests that the workflow is properly configured for HTTP mode.
"""
import os
import sys
import requests
import time
import argparse

def check_ssl_enabled():
    """Check if SSL is enabled in the environment"""
    ssl_enabled = os.environ.get('SSL_ENABLED', 'false').lower() == 'true'
    http_only = os.environ.get('HTTP_ONLY', 'false').lower() == 'true'
    
    print(f"SSL_ENABLED: {os.environ.get('SSL_ENABLED', 'Not set')}")
    print(f"HTTP_ONLY: {os.environ.get('HTTP_ONLY', 'Not set')}")
    
    if ssl_enabled:
        print("⚠️ WARNING: SSL is enabled, which might cause problems with Replit's load balancer")
        return False
    elif http_only:
        print("✓ HTTP-only mode is enabled, which is correct for Replit's load balancer")
        return True
    else:
        print("⚠️ WARNING: Neither SSL_ENABLED nor HTTP_ONLY is explicitly set")
        return False

def test_replit_domain():
    """Test if the Replit domain is accessible via HTTP"""
    replit_domain = os.environ.get('REPLIT_DEV_DOMAIN', None)
    
    if not replit_domain:
        print("⚠️ WARNING: REPLIT_DEV_DOMAIN environment variable not set")
        return False
    
    print(f"Testing HTTP access to {replit_domain}...")
    
    # Try both HTTP and HTTPS
    http_url = f"http://{replit_domain}/health"
    https_url = f"https://{replit_domain}/health"
    
    # Test HTTP
    try:
        response = requests.get(http_url, timeout=5)
        print(f"HTTP access: {response.status_code}")
        http_works = response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"HTTP access failed: {e}")
        http_works = False
    
    # Test HTTPS
    try:
        response = requests.get(https_url, timeout=5)
        print(f"HTTPS access: {response.status_code}")
        https_works = response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"HTTPS access failed: {e}")
        https_works = False
    
    # Evaluate results
    if https_works and not http_works:
        print("✓ HTTPS works but HTTP doesn't - this is expected with Replit's load balancer")
        return True
    elif http_works and https_works:
        print("✓ Both HTTP and HTTPS work - this might be due to Replit's load balancer")
        return True
    elif http_works and not https_works:
        print("⚠️ WARNING: HTTP works but HTTPS doesn't - this is not expected")
        return False
    else:
        print("⚠️ WARNING: Neither HTTP nor HTTPS works - the server might not be running")
        return False

def main():
    """Run HTTP workflow tests"""
    parser = argparse.ArgumentParser(description="Test HTTP workflow configuration")
    parser.add_argument("--skip-remote", action="store_true", 
                        help="Skip testing remote domain (only check environment)")
    args = parser.parse_args()
    
    print("=== HTTP Workflow Test ===")
    
    success = check_ssl_enabled()
    
    if not args.skip_remote:
        success = test_replit_domain() and success
    
    if success:
        print("\nAll tests passed successfully!")
        return 0
    else:
        print("\nSome tests failed. Please check the warnings above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
