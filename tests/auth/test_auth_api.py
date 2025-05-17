#!/usr/bin/env python3
"""
Test script for authentication API endpoints.
This script tests all the authentication endpoints and provides a simple
way to verify they're working correctly.

Usage:
    python test_auth_api.py [hostname] [--no-ssl]

Examples:
    # Local HTTPS development (default)
    python test_auth_api.py
    
    # Local HTTP development
    python test_auth_api.py --no-ssl
    
    # Remote server
    python test_auth_api.py http://example.com
    
    # Remote secure server
    python test_auth_api.py https://example.com
"""

import sys
import requests
import json
import os
from urllib.parse import urljoin

# Default to HTTPS for local development
use_ssl = True

# Process command line arguments
args = sys.argv[1:]
# Default base URL, can be overridden with command line argument
BASE_URL = 'localhost:5000'

# Parse command line arguments
for arg in args:
    if arg == '--no-ssl':
        use_ssl = False
        args.remove(arg)
        break

# If a hostname is provided as first argument, use it
if args and not args[0].startswith('--'):
    BASE_URL = args[0]
    # Check if the provided URL already includes a protocol
    if not BASE_URL.startswith(('http://', 'https://')):
        # If no protocol, use the one determined by use_ssl
        protocol = 'https://' if use_ssl else 'http://'
        BASE_URL = protocol + BASE_URL
else:
    # No hostname provided, use default with appropriate protocol
    protocol = 'https://' if use_ssl else 'http://'
    BASE_URL = protocol + BASE_URL

print(f"Testing API endpoints at: {BASE_URL}")

# Set to store cookies from requests
session = requests.Session()

# Disable SSL verification for local development with self-signed certificates
if BASE_URL.startswith('https://localhost'):
    session.verify = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("SSL verification disabled for local testing")

def print_response(response):
    """Print response details in a readable format."""
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print(response.text)
    print("-" * 50)

def test_csrf_endpoint():
    """Test the CSRF token endpoint."""
    print("\n[Testing CSRF Token Endpoint]")
    response = session.get(urljoin(BASE_URL, '/api/auth/csrf/'))
    print_response(response)
    return response.json().get('csrfToken')

def test_session_check_endpoint():
    """Test the session check endpoint."""
    print("\n[Testing Session Check Endpoint]")
    response = session.get(urljoin(BASE_URL, '/api/auth/session/'))
    print_response(response)
    return response.status_code == 200

def test_user_endpoint():
    """Test the user profile endpoint."""
    print("\n[Testing User Profile Endpoint]")
    response = session.get(urljoin(BASE_URL, '/api/auth/user/'))
    print_response(response)
    return response.status_code == 200

def login_user(username, password, csrf_token):
    """Attempt to log in a user."""
    print("\n[Attempting Login]")
    headers = {'X-CSRFToken': csrf_token}
    data = {
        'login': username,
        'password': password,
        'csrfmiddlewaretoken': csrf_token
    }
    response = session.post(
        urljoin(BASE_URL, '/accounts/login/'),
        headers=headers,
        data=data
    )
    print_response(response)
    return response.status_code == 200 or response.status_code == 302

def logout_user(csrf_token):
    """Attempt to log out a user."""
    print("\n[Attempting Logout]")
    headers = {'X-CSRFToken': csrf_token}
    response = session.post(
        urljoin(BASE_URL, '/api/auth/logout/'),
        headers=headers
    )
    print_response(response)
    return response.status_code == 200

def main():
    global BASE_URL
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]

    print(f"Testing authentication endpoints at {BASE_URL}")
    
    # Test CSRF token endpoint
    csrf_token = test_csrf_endpoint()
    if not csrf_token:
        print("Failed to get CSRF token")
        return
    
    # Test session check endpoint (should be unauthenticated)
    is_authenticated = test_session_check_endpoint()
    
    # If not authenticated, prompt for login
    if not is_authenticated:
        print("\nNot currently authenticated. Would you like to try logging in? (y/n)")
        choice = input().lower()
        if choice == 'y':
            username = input("Username: ")
            password = input("Password: ")
            login_successful = login_user(username, password, csrf_token)
            
            if login_successful:
                print("\nLogin appears successful. Checking user endpoint...")
                # Get a new CSRF token
                csrf_token = test_csrf_endpoint()
                # Test session check again
                test_session_check_endpoint()
                # Test user endpoint
                test_user_endpoint()
                
                # Ask if user wants to logout
                print("\nWould you like to logout? (y/n)")
                choice = input().lower()
                if choice == 'y':
                    logout_user(csrf_token)
                    # Check session again
                    test_session_check_endpoint()
            else:
                print("\nLogin failed.")
    else:
        print("\nAlready authenticated.")
        # Test user endpoint
        test_user_endpoint()
        
        # Ask if user wants to logout
        print("\nWould you like to logout? (y/n)")
        choice = input().lower()
        if choice == 'y':
            logout_user(csrf_token)
            # Check session again
            test_session_check_endpoint()

if __name__ == "__main__":
    main()