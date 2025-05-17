#!/usr/bin/env python3
"""
Test script for API authentication.
This script verifies that API authentication is working correctly.
"""
import os
import sys
import requests
import argparse
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default URLs for testing
DEFAULT_BASE_URL = "http://localhost:5000"
DEFAULT_API_URL = f"{DEFAULT_BASE_URL}/api"
DEFAULT_AUTH_URL = f"{DEFAULT_API_URL}/auth"

def get_csrf_token(base_url):
    """Get a CSRF token from the server"""
    csrf_url = f"{base_url}/api/csrf/"
    
    try:
        response = requests.get(csrf_url)
        
        if response.status_code == 200:
            data = response.json()
            csrf_token = data.get('csrfToken')
            
            if csrf_token:
                logger.info(f"Successfully obtained CSRF token: {csrf_token[:6]}...")
                return csrf_token, response.cookies
            else:
                logger.error("CSRF token not found in response")
                return None, None
        else:
            logger.error(f"Failed to get CSRF token: {response.status_code}")
            return None, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting CSRF token: {e}")
        return None, None

def login(base_url, username, password, csrf_token, cookies):
    """Log in with the given credentials"""
    login_url = f"{base_url}/api/auth/login/"
    
    # Prepare login data
    login_data = {
        'username': username,
        'password': password
    }
    
    # Prepare headers with CSRF token
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            login_url, 
            data=json.dumps(login_data),
            headers=headers,
            cookies=cookies
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully logged in as {username}")
            return True, response.cookies
        else:
            logger.error(f"Login failed: {response.status_code} - {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during login: {e}")
        return False, None

def check_authenticated(base_url, cookies):
    """Check if the current session is authenticated"""
    session_url = f"{base_url}/api/auth/session/"
    
    try:
        response = requests.get(session_url, cookies=cookies)
        
        if response.status_code == 200:
            data = response.json()
            is_authenticated = data.get('isAuthenticated', False)
            
            if is_authenticated:
                username = data.get('username', 'unknown')
                logger.info(f"Session is authenticated as {username}")
                return True
            else:
                logger.error("Session check failed: Not authenticated")
                return False
        else:
            logger.error(f"Session check failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking session: {e}")
        return False

def main():
    """Run API authentication tests"""
    parser = argparse.ArgumentParser(description="Test API authentication")
    parser.add_argument("--url", default=DEFAULT_BASE_URL, help="Base URL for testing")
    parser.add_argument("--username", default="admin", help="Username for login test")
    parser.add_argument("--password", default="admin", help="Password for login test")
    args = parser.parse_args()
    
    logger.info("=== API Authentication Test ===")
    
    # Get CSRF token
    logger.info("Getting CSRF token...")
    csrf_token, cookies = get_csrf_token(args.url)
    
    if not csrf_token:
        logger.error("Failed to get CSRF token, aborting tests")
        return 1
    
    # Login
    logger.info(f"Attempting to log in as {args.username}...")
    login_success, auth_cookies = login(args.url, args.username, args.password, csrf_token, cookies)
    
    if not login_success:
        logger.error("Login failed, aborting tests")
        return 1
    
    # Check authentication
    logger.info("Checking authentication status...")
    auth_check = check_authenticated(args.url, auth_cookies)
    
    if auth_check:
        logger.info("\nAPI authentication tests passed successfully!")
        return 0
    else:
        logger.error("\nAPI authentication tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
