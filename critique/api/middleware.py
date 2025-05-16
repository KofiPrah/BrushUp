"""
Middleware for the Art Critique API.
"""
import json
from django.utils.deprecation import MiddlewareMixin
from .image_url_fix import fix_relative_image_urls

class FixImageUrlsMiddleware(MiddlewareMixin):
    """
    Middleware that fixes relative image URLs in API responses by converting them to absolute URLs.
    This will process all JSON responses from API endpoints.
    """
    
    def process_response(self, request, response):
        """
        Process the response to fix any relative image URLs.
        
        Args:
            request: The request object
            response: The response object
            
        Returns:
            The processed response object
        """
        # Only process API responses
        if not request.path.startswith('/api/'):
            return response
            
        # Only process JSON responses
        content_type = response.get('Content-Type', '')
        if 'application/json' not in content_type:
            return response
            
        try:
            # Decode the JSON content
            content = response.content.decode('utf-8')
            data = json.loads(content)
            
            # Fix the image URLs
            fixed_data = fix_relative_image_urls(data)
            
            # Encode the fixed data back to JSON
            fixed_content = json.dumps(fixed_data)
            response.content = fixed_content.encode('utf-8')
            
            # Update the Content-Length header
            response['Content-Length'] = len(response.content)
        except Exception as e:
            # Log the error but don't break the response
            print(f"Error fixing image URLs: {e}")
            
        return response