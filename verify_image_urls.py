#!/usr/bin/env python
"""
Script to verify image URLs in artwork API responses
"""
import os
import requests
from urllib.parse import urlparse

# Suppress SSL warnings for this test
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://brushup.replit.app"
ARTWORK_LIST_URL = f"{BASE_URL}/api/artworks/"
ARTWORK_DETAIL_URL = f"{BASE_URL}/api/artworks/21/"  # Specific artwork ID to check

def check_url_accessibility(url):
    """Check if a URL is accessible"""
    if not url:
        return False, "No URL provided"
    
    try:
        # Skip SSL verification for testing
        response = requests.head(url, verify=False, timeout=10)
        return response.status_code == 200, f"Status code: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_artwork_list():
    """Check artwork list endpoint and image URLs"""
    print(f"\n--- Checking artwork list endpoint: {ARTWORK_LIST_URL} ---")
    
    try:
        response = requests.get(ARTWORK_LIST_URL, verify=False)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return
        
        artworks = response.json()
        print(f"Found {len(artworks)} artworks in the list")
        
        for i, artwork in enumerate(artworks[:5]):  # Check first 5 artworks
            print(f"\nArtwork #{i+1}: {artwork.get('title', 'Untitled')}")
            
            # Check image URL
            image_url = artwork.get('image_display_url')
            if not image_url:
                print("No image_display_url found")
                continue
                
            print(f"Image URL: {image_url}")
            
            # Parse URL to understand storage type
            parsed_url = urlparse(image_url)
            if 's3.amazonaws.com' in parsed_url.netloc:
                print("Storage type: AWS S3")
            elif parsed_url.path.startswith('/media/'):
                print("Storage type: Local storage")
            else:
                print(f"Storage type: Unknown ({parsed_url.netloc})")
            
            # Check accessibility
            accessible, message = check_url_accessibility(image_url)
            if accessible:
                print("✓ Image is accessible")
            else:
                print(f"✗ Image is not accessible: {message}")
    
    except Exception as e:
        print(f"Error checking artwork list: {str(e)}")

def check_artwork_detail():
    """Check artwork detail endpoint and image URL"""
    print(f"\n--- Checking artwork detail endpoint: {ARTWORK_DETAIL_URL} ---")
    
    try:
        response = requests.get(ARTWORK_DETAIL_URL, verify=False)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return
        
        artwork = response.json()
        print(f"Artwork: {artwork.get('title', 'Untitled')}")
        
        # Check image URL
        image_url = artwork.get('image_display_url')
        if not image_url:
            print("No image_display_url found")
            return
            
        print(f"Image URL: {image_url}")
        
        # Parse URL to understand storage type
        parsed_url = urlparse(image_url)
        if 's3.amazonaws.com' in parsed_url.netloc:
            print("Storage type: AWS S3")
        elif parsed_url.path.startswith('/media/'):
            print("Storage type: Local storage")
        else:
            print(f"Storage type: Unknown ({parsed_url.netloc})")
        
        # Check accessibility
        accessible, message = check_url_accessibility(image_url)
        if accessible:
            print("✓ Image is accessible")
        else:
            print(f"✗ Image is not accessible: {message}")
    
    except Exception as e:
        print(f"Error checking artwork detail: {str(e)}")

def main():
    """Main function"""
    print("=== Artwork Image URL Verification ===")
    print(f"Base URL: {BASE_URL}")
    
    check_artwork_list()
    check_artwork_detail()

if __name__ == "__main__":
    main()