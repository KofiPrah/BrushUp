#!/usr/bin/env python
"""
Simple script to test if the local image storage is working properly.
This will create a test image and upload it to make sure it can be displayed.
"""
import os
import json
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests


def create_test_image(filename="test_local_storage.jpg", size_kb=20):
    """
    Create a simple test image for upload testing.
    """
    print(f"Creating test image: {filename}")
    
    # Create a new image with a random color
    image_size = (400, 300)
    color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )
    
    # Create an image with the random color
    img = Image.new('RGB', image_size, color=color)
    
    # Add some text
    draw = ImageDraw.Draw(img)
    text = "Test Image"
    
    # Calculate text position (centered)
    text_x = image_size[0] // 2 - len(text) * 4
    text_y = image_size[1] // 2 - 10
    
    # Draw text with white color
    draw.text((text_x, text_y), text, fill=(255, 255, 255))
    
    # Draw a border
    draw.rectangle(
        [(0, 0), (image_size[0] - 1, image_size[1] - 1)],
        outline=(255, 255, 255)
    )
    
    # Save to a file
    if os.path.exists(filename):
        os.remove(filename)
    
    img.save(filename, quality=95)
    
    print(f"Test image created: {filename}")
    return filename


def get_csrf_token():
    """
    Get a CSRF token from the API.
    """
    url = "http://localhost:8000/api/csrf-token/"
    response = requests.get(url)
    return response.cookies.get("csrftoken")


def login(username, password, csrf_token):
    """
    Log in to get a session cookie.
    """
    url = "http://localhost:8000/api/login/"
    headers = {"X-CSRFToken": csrf_token}
    data = {"username": username, "password": password}
    
    response = requests.post(
        url, 
        json=data, 
        headers=headers, 
        cookies={"csrftoken": csrf_token}
    )
    
    # Check if login was successful
    if response.status_code == 200:
        print(f"Login successful for {username}")
        return response.cookies
    else:
        print(f"Login failed: {response.text}")
        return None


def upload_image(csrf_token, cookies, filename):
    """
    Upload a test image to test local storage.
    """
    url = "http://localhost:8000/api/artworks/"
    
    # Prepare the image file
    with open(filename, "rb") as f:
        files = {"image": (filename, f, "image/jpeg")}
        
        # Prepare the artwork data
        data = {
            "title": "Local Storage Test",
            "description": "Testing local storage image display",
            "medium": "Digital",
            "dimensions": "400x300",
            "tags": "test,local-storage,debugging"
        }
        
        # Upload the artwork
        headers = {"X-CSRFToken": csrf_token}
        response = requests.post(
            url,
            data=data,
            files=files,
            headers=headers,
            cookies=cookies
        )
    
    # Check if upload was successful
    if response.status_code in (200, 201):
        print("Upload successful!")
        return response.json()
    else:
        print(f"Upload failed: {response.status_code}")
        print(response.text)
        return None


def main():
    """
    Run the full test for local storage image display.
    """
    # Create test image
    filename = create_test_image()
    
    # Get server URL from Replit environment
    server_url = "https://0.0.0.0:5000"
    
    # Get CSRF token
    print(f"Getting CSRF token from {server_url}/api/csrf-token/")
    
    # Make API URL dynamic based on environment
    csrf_url = f"{server_url}/api/csrf-token/"
    login_url = f"{server_url}/api/login/"
    upload_url = f"{server_url}/api/artworks/"
    
    # Get CSRF token - disable SSL verification for self-signed certificate
    print("Warning: Disabling SSL verification for testing purposes only")
    csrf_response = requests.get(csrf_url, verify=False)
    csrf_token = csrf_response.cookies.get("csrftoken")
    
    if not csrf_token:
        print("Failed to get CSRF token. Check if the server is running.")
        return
    
    print(f"Got CSRF token: {csrf_token[:10]}...")
    
    # Login
    headers = {"X-CSRFToken": csrf_token}
    login_data = {"username": "admin", "password": "password123"}
    
    login_response = requests.post(
        login_url, 
        json=login_data, 
        headers=headers, 
        cookies={"csrftoken": csrf_token},
        verify=False  # Disable SSL verification
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    print("Login successful!")
    cookies = login_response.cookies
    
    # Upload image
    with open(filename, "rb") as f:
        files = {"image": (filename, f, "image/jpeg")}
        
        # Prepare the artwork data
        data = {
            "title": "Local Storage Test",
            "description": "Testing local storage image display",
            "medium": "Digital",
            "dimensions": "400x300",
            "tags": "test,local-storage,debugging"
        }
        
        # Upload the artwork
        headers = {"X-CSRFToken": csrf_token}
        upload_response = requests.post(
            upload_url,
            data=data,
            files=files,
            headers=headers,
            cookies=cookies,
            verify=False  # Disable SSL verification
        )
    
    # Check if upload was successful
    if upload_response.status_code in (200, 201):
        print("Upload successful!")
        result = upload_response.json()
        print(f"Artwork ID: {result.get('id')}")
        print(f"Image URL: {result.get('image_display_url')}")
        
        # Verify image is accessible
        if result.get('image_display_url'):
            img_response = requests.get(result.get('image_display_url'), verify=False)
            if img_response.status_code == 200:
                print("Image is accessible via the URL!")
            else:
                print(f"Image access failed: {img_response.status_code}")
        else:
            print("No image URL was returned.")
    else:
        print(f"Upload failed: {upload_response.status_code}")
        print(upload_response.text)


if __name__ == "__main__":
    main()