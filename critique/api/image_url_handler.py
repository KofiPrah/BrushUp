"""
A utility module for handling image URLs in the Art Critique application.
This is a specialized solution to make sure images are accessible in all environments.
"""
from django.conf import settings
import os

def get_absolute_media_url(relative_path):
    """
    Convert a relative media path to an absolute URL.
    This handles both local development and production environments.
    
    Args:
        relative_path: A relative path like 'artworks/image.jpg' or '/media/artworks/image.jpg'
        
    Returns:
        An absolute URL to the media file
    """
    if not relative_path:
        return ""
        
    # Strip leading slash if present
    if relative_path.startswith('/'):
        relative_path = relative_path[1:]
        
    # Strip media prefix if present
    if relative_path.startswith('media/'):
        relative_path = relative_path[6:]
        
    # Get the site domain from settings or environment
    domain = getattr(settings, 'SITE_DOMAIN', None)
    if not domain:
        # Default to the Replit app domain
        domain = "https://brushup.replit.app"
        
    # Construct the full URL
    return f"{domain}/media/{relative_path}"

def add_image_urls(serializer_class):
    """
    Decorator for serializer classes to add image URL handling.
    
    This adds a method to generate absolute URLs for image fields.
    
    Args:
        serializer_class: The serializer class to enhance
        
    Returns:
        The enhanced serializer class
    """
    original_to_representation = serializer_class.to_representation
    
    def enhanced_to_representation(self, instance):
        # First get the original representation
        data = original_to_representation(self, instance)
        
        # Check for image fields and ensure they have proper URLs
        for field_name in ['image', 'profile_picture']:
            if field_name in data and data[field_name]:
                # Get the image URL in display format
                display_url_field = f"{field_name}_display_url"
                
                # If already an absolute URL, keep it
                if data.get(display_url_field) and (
                    data[display_url_field].startswith('http://') or 
                    data[display_url_field].startswith('https://')
                ):
                    continue
                    
                # Otherwise, set the display URL field
                if field_name in data and data[field_name]:
                    data[display_url_field] = get_absolute_media_url(data[field_name])
                    
        return data
        
    # Replace the to_representation method
    serializer_class.to_representation = enhanced_to_representation
    
    return serializer_class