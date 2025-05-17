#!/usr/bin/env python3
"""
Test script for HTTP server functionality.
Verifies that the application works properly in HTTP mode.
"""
import os
import sys
import time
import requests
import argparse

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Default URLs
DEFAULT_URL = "http://localhost:5000"
DEFAULT_HEALTH_URL = f"{DEFAULT_URL}/health"

def check_server_health(health_url=DEFAULT_HEALTH_URL, retries=5, delay=1):
    """Check if the server is running and healthy"""
    print(f"Checking server health at {health_url}...")
    
    for i in range(retries):
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                print("Server is healthy!")
                return True
            else:
                print(f"  Health check failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  Connection error: {e}")
        
        if i < retries - 1:
            print(f"  Retrying in {delay} seconds...")
            time.sleep(delay)
    
    print("Server health check failed after multiple attempts")
    return False

def test_basic_routes(base_url=DEFAULT_URL):
    """Test basic routes to verify server functionality"""
    print(f"Testing basic routes at {base_url}...")
    
    routes = {
        "/": {
            "name": "Root redirect",
            "method": "GET",
            "expected_status": [301, 302, 307, 308]  # Redirect status codes
        },
        "/health": {
            "name": "Health check",
            "method": "GET",
            "expected_status": [200]
        },
        "/admin/": {
            "name": "Admin page",
            "method": "GET",
            "expected_status": [200, 302]  # 200 or redirect to login
        }
    }
    
    success_count = 0
    
    for route, config in routes.items():
        url = f"{base_url}{route}"
        print(f"  Testing {config['name']} ({url})...")
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in config['expected_status']:
                print(f"    ✓ Success! Status code: {response.status_code}")
                success_count += 1
            else:
                print(f"    ✗ Failure. Expected {config['expected_status']}, got {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"    ✗ Error: {e}")
    
    print(f"Route test results: {success_count}/{len(routes)} successful")
    return success_count == len(routes)

def main():
    """Run HTTP server tests"""
    parser = argparse.ArgumentParser(description="Test HTTP server functionality")
    parser.add_argument("--url", default=DEFAULT_URL, help="Base URL for testing")
    parser.add_argument("--no-health", action="store_true", help="Skip health check")
    args = parser.parse_args()
    
    print("=== HTTP Server Test ===")
    
    success = True
    
    if not args.no_health:
        health_url = f"{args.url}/health"
        success = success and check_server_health(health_url)
    
    success = success and test_basic_routes(args.url)
    
    if success:
        print("\nAll tests passed successfully!")
        return 0
    else:
        print("\nSome tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())