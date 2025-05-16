"""
Utility to handle missing image files gracefully in the Art Critique application.
"""
import os
from django.conf import settings

# Define a placeholder image URL to use when the actual image is missing
PLACEHOLDER_IMAGE_URL = "https://via.placeholder.com/800x600?text=Image+Unavailable"

def get_image_url(image_path):
    """
    Check if an image file exists and return an appropriate URL.
    
    Args:
        image_path: The path to the image file
        
    Returns:
        URL to the image if it exists, otherwise placeholder image URL
    """
    if not image_path:
        return PLACEHOLDER_IMAGE_URL
        
    # If it's already a full URL not pointing to our media server, return it as is
    if image_path.startswith('http') and not '/media/' in image_path:
        return image_path
        
    # If it's a relative path, convert to an absolute path
    if image_path.startswith('/'):
        # Remove leading slash from media URL
        if image_path.startswith('/media/'):
            rel_path = image_path[7:]  # Remove /media/ prefix
        else:
            rel_path = image_path[1:]  # Remove leading slash
            
        # Get the absolute file path
        file_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    # If it's already a relative path without leading slash
    else:
        file_path = os.path.join(settings.MEDIA_ROOT, image_path)
        
    # Check if the file exists
    if os.path.exists(file_path):
        # File exists, return URL to the real image
        site_domain = getattr(settings, 'SITE_DOMAIN', 'https://brushup.replit.app')
        if image_path.startswith('/'):
            return f"{site_domain}{image_path}"
        else:
            return f"{site_domain}/media/{image_path}"
    else:
        # File doesn't exist, return placeholder
        return PLACEHOLDER_IMAGE_URL