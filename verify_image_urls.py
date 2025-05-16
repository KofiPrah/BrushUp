#!/usr/bin/env python
"""
Script to verify image URLs in artwork API responses
"""
import os
import json
import requests
from urllib.parse import urlparse

# Suppress SSL warnings for testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://brushup.replit.app"
ARTWORK_LIST_URL = f"{BASE_URL}/api/artworks/"
ARTWORK_DETAIL_URL = f"{BASE_URL}/api/artworks/21/"  # Specific artwork ID to check

def print_header(text):
    """Print formatted header text"""
    print("\n" + "=" * 40)
    print(text)
    print("=" * 40)

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
    print_header("Checking artwork list endpoint")
    print(f"URL: {ARTWORK_LIST_URL}")
    
    try:
        response = requests.get(ARTWORK_LIST_URL, verify=False)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
            return
        
        artworks = response.json()
        
        if isinstance(artworks, dict) and 'results' in artworks:
            # Paginated response
            print(f"Found {artworks.get('count', 0)} artworks in paginated response")
            artworks = artworks.get('results', [])
        else:
            print(f"Found {len(artworks)} artworks in list")
        
        for i, artwork in enumerate(artworks[:5]):  # Check first 5 artworks
            print(f"\nArtwork #{i+1}: {artwork.get('title', 'Untitled')}")
            
            # Check image URL
            image_url = artwork.get('image_display_url')
            if not image_url:
                print("❌ No image_display_url found")
                continue
                
            print(f"Image URL: {image_url}")
            
            # Check if URL is absolute (has scheme)
            parsed_url = urlparse(image_url)
            if not parsed_url.scheme:
                print("❌ URL is relative, not absolute")
            else:
                print("✅ URL is absolute")
            
            # Parse URL to understand storage type
            if parsed_url.netloc and 's3.amazonaws.com' in parsed_url.netloc:
                print("Storage type: AWS S3")
            elif parsed_url.path and parsed_url.path.startswith('/media/'):
                print("Storage type: Local storage")
            else:
                print(f"Storage type: Unknown ({parsed_url.netloc})")
            
            # Check accessibility
            if parsed_url.scheme:  # Only check if URL is absolute
                accessible, message = check_url_accessibility(image_url)
                if accessible:
                    print("✅ Image is accessible")
                else:
                    print(f"❌ Image is not accessible: {message}")
    
    except Exception as e:
        print(f"Error checking artwork list: {str(e)}")

def check_artwork_detail():
    """Check artwork detail endpoint and image URL"""
    print_header("Checking artwork detail endpoint")
    print(f"URL: {ARTWORK_DETAIL_URL}")
    
    try:
        response = requests.get(ARTWORK_DETAIL_URL, verify=False)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
            return
        
        # Pretty print the response data
        artwork = response.json()
        print(f"Artwork: {artwork.get('title', 'Untitled')}")
        
        # Check image URL
        image_url = artwork.get('image_display_url')
        if not image_url:
            print("❌ No image_display_url found")
            return
            
        print(f"Image URL: {image_url}")
        
        # Check if URL is absolute (has scheme)
        parsed_url = urlparse(image_url)
        if not parsed_url.scheme:
            print("❌ URL is relative, not absolute")
        else:
            print("✅ URL is absolute")
        
        # Parse URL to understand storage type
        if parsed_url.netloc and 's3.amazonaws.com' in parsed_url.netloc:
            print("Storage type: AWS S3")
        elif parsed_url.path and parsed_url.path.startswith('/media/'):
            print("Storage type: Local storage")
        else:
            print(f"Storage type: Unknown ({parsed_url.netloc})")
        
        # Check accessibility
        if parsed_url.scheme:  # Only check if URL is absolute
            accessible, message = check_url_accessibility(image_url)
            if accessible:
                print("✅ Image is accessible")
            else:
                print(f"❌ Image is not accessible: {message}")
                
        # Save response data to file for inspection
        with open('artwork_detail_response.json', 'w') as f:
            json.dump(artwork, f, indent=2)
        print("Saved response data to artwork_detail_response.json")
    
    except Exception as e:
        print(f"Error checking artwork detail: {str(e)}")

def main():
    """Main function"""
    print_header("Artwork Image URL Verification")
    print(f"Base URL: {BASE_URL}")
    
    # Run the checks
    check_artwork_list()
    check_artwork_detail()

if __name__ == "__main__":
    main()