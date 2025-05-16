"""
Test script for image upload with session authentication and CSRF token handling
"""
import os
import requests
import json
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://0.0.0.0:5000"  # Use local address without HTTPS
TEST_IMAGE = "test_image.jpg"
USERNAME = "test_s3_user"  # Use the existing test user created in our S3 test
PASSWORD = "testpassword123"

# Create a session to maintain cookies
session = requests.Session()

def create_test_image():
    """Create a simple test image if one doesn't exist"""
    if not os.path.exists(TEST_IMAGE):
        print(f"Creating test image: {TEST_IMAGE}")
        # Create a minimal valid JPEG file
        with open(TEST_IMAGE, 'wb') as f:
            # JPEG SOI marker
            f.write(bytes.fromhex('FFD8'))
            # JPEG APP0 marker
            f.write(bytes.fromhex('FFE0'))
            # Length of APP0 segment
            f.write(bytes.fromhex('0010'))
            # JFIF identifier
            f.write(b'JFIF\x00')
            # Version
            f.write(bytes.fromhex('0101'))
            # Units, X density, Y density
            f.write(bytes.fromhex('0001 0001 0001'))
            # Thumbnail width and height (0x0)
            f.write(bytes.fromhex('0000'))
            # JPEG EOI marker
            f.write(bytes.fromhex('FFD9'))
        print(f"Test image created: {TEST_IMAGE}")
    else:
        print(f"Using existing test image: {TEST_IMAGE}")

def get_csrf_token():
    """Get CSRF token from the API"""
    print("\n=== Getting CSRF Token ===")
    try:
        # Use the correct CSRF token endpoint based on API documentation
        response = session.get(urljoin(BASE_URL, "/api/auth/csrf/"), headers={
            "Referer": BASE_URL
        })
        
        if response.status_code == 200:
            csrf_token = response.json().get('csrfToken')
            print(f"✓ Got CSRF token: {csrf_token[:10]}..." if csrf_token else "❌ No csrfToken in response")
            
            # Show all cookies
            print("Current cookies:")
            for cookie_name, cookie_value in session.cookies.items():
                masked_value = str(cookie_value)
                if len(masked_value) > 10:
                    masked_value = masked_value[:10] + "..."
                print(f"  - {cookie_name}: {masked_value}")
                
            return csrf_token
        else:
            print(f"❌ Failed to get CSRF token: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error getting CSRF token: {str(e)}")
        return None

def login(username, password, csrf_token):
    """Log in to get session authentication"""
    print(f"\n=== Logging in as {username} ===")
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        # Add the CSRF token to headers
        headers = {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
            "Referer": BASE_URL
        }
        
        print(f"Sending login request to {urljoin(BASE_URL, '/api/auth/login/')}")
        response = session.post(
            urljoin(BASE_URL, "/api/auth/login/"),
            headers=headers,
            json=login_data
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if 'user' in response_data:
                user_data = response_data['user']
                print(f"✓ Successfully logged in as: {user_data.get('username', 'unknown')}")
            else:
                print(f"✓ Successfully logged in (but unexpected response format)")
                print(f"Response data: {response_data}")
            
            # Show all cookies after login
            print("Cookies after login:")
            for cookie_name, cookie_value in session.cookies.items():
                masked_value = str(cookie_value)
                if len(masked_value) > 10:
                    masked_value = masked_value[:10] + "..."
                print(f"  - {cookie_name}: {masked_value}")
                
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_auth_session():
    """Check if the user session is valid"""
    print("\n=== Checking Auth Session ===")
    try:
        # Use the correct session check endpoint based on API documentation
        response = session.get(urljoin(BASE_URL, "/api/auth/session/"), headers={
            "Referer": BASE_URL
        })
        
        if response.status_code == 200:
            user_data = response.json()
            # Check if response indicates we're authenticated
            if user_data.get('auth_info', {}).get('is_authenticated', False):
                print(f"✓ Session valid - Logged in as: {user_data.get('username', 'unknown')}")
                return True
            else:
                print(f"❌ Session not authenticated: {user_data}")
                return False
        else:
            print(f"❌ Session check failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error checking session: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def upload_image(csrf_token):
    """Upload a test image to the API"""
    print("\n=== Uploading Test Image ===")
    
    # Create test image if needed
    create_test_image()
    
    # Prepare the artwork data
    artwork_data = {
        "title": "Test Artwork for S3 Integration",
        "description": "This is a test artwork to verify S3 integration",
        "medium": "Digital",
        "dimensions": "800x600",
        "tags": "test,s3,integration"
    }
    
    # Prepare the file for upload
    files = {
        'image': (os.path.basename(TEST_IMAGE), open(TEST_IMAGE, 'rb')),
    }
    
    # Add other fields to the form data
    form_data = {key: value for key, value in artwork_data.items()}
    
    print("Uploading test image with the following details:")
    for key, value in artwork_data.items():
        print(f"  - {key}: {value}")
    
    try:
        # Debug headers
        headers = {
            "X-CSRFToken": csrf_token,
            "Referer": BASE_URL
        }
        print("Using headers:")
        for key, value in headers.items():
            print(f"  - {key}: {value}")
            
        # Debug cookies
        print("Using cookies:")
        for cookie_name, cookie_value in session.cookies.items():
            print(f"  - {cookie_name}: {cookie_value[:10]}...")
        
        upload_response = session.post(
            urljoin(BASE_URL, "/api/artworks/"),
            data=form_data,
            files=files,
            headers=headers
        )
        
        if upload_response.status_code in (200, 201):
            response_data = upload_response.json()
            print("✓ Upload successful!")
            print(f"✓ Artwork ID: {response_data.get('id', 'unknown')}")
            
            if 'image' in response_data:
                image_url = response_data['image']
                print(f"✓ Image URL: {image_url}")
                
                # Check if the URL points to S3
                if "s3.amazonaws.com" in image_url:
                    print("✓ Image is stored in S3 bucket!")
                else:
                    print("✓ Image is stored on local storage")
            else:
                print("❌ No image URL in the response")
                
            return response_data
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(upload_response.text)
            return None
    except Exception as e:
        print(f"❌ Error during upload: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run the full authentication and upload test"""
    print("=== Art Critique Authentication & Image Upload Test ===")
    
    # Step 1: Get CSRF token
    csrf_token = get_csrf_token()
    if not csrf_token:
        print("❌ Cannot proceed without CSRF token")
        return
    
    # Step 2: Log in
    login_success = login(USERNAME, PASSWORD, csrf_token)
    if not login_success:
        print("❌ Login failed - trying to continue anyway")
    
    # Step 3: Check session
    session_valid = check_auth_session()
    if not session_valid:
        print("❌ Invalid authentication session - trying to continue anyway")
    
    # Step 4: Upload image
    print("\nAttempting image upload...")
    result = upload_image(csrf_token)
    
    if result:
        print("\n✅ TEST SUCCESSFUL: Image upload successful!")
    else:
        print("\n❌ TEST FAILED: Image upload failed!")
        
    print("\nTest completed!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()