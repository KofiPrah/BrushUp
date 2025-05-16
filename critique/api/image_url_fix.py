"""
This module provides a utility function to fix relative image URLs in the API responses.
"""

def fix_relative_image_urls(response_data):
    """
    Recursively process API response data and convert any relative image URLs to absolute URLs.
    
    Args:
        response_data: The API response data (can be a dict, list, or other data type)
        
    Returns:
        The processed response data with fixed image URLs
    """
    # Hard-code the domain for Replit app
    domain = "https://brushup.replit.app"
    
    if isinstance(response_data, dict):
        # Process each key in the dictionary
        for key, value in response_data.items():
            # Check if this is an image URL field
            if key in ('image_url', 'image_display_url') and isinstance(value, str):
                # Convert relative URLs to absolute URLs
                if value and value.startswith('/'):
                    response_data[key] = f"{domain}{value}"
            # Recursively process nested dictionaries and lists
            elif isinstance(value, (dict, list)):
                response_data[key] = fix_relative_image_urls(value)
    
    elif isinstance(response_data, list):
        # Process each item in the list
        for i, item in enumerate(response_data):
            response_data[i] = fix_relative_image_urls(item)
    
    return response_data