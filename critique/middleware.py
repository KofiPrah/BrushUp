"""
Custom middleware for BrushUp project to handle Replit-specific environment issues.
"""

from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ReplitCSRFMiddleware(CsrfViewMiddleware):
    """
    Custom CSRF middleware that's more lenient for Replit preview environments.
    This helps with iframe and proxy issues that can prevent CSRF tokens from working.
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Check if we're in a Replit preview environment
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')
        
        # If it's a Replit preview request, be more lenient
        if ('replit' in referer.lower() or 
            'headlesschrome' in user_agent.lower() or
            request.META.get('HTTP_X_REPLIT_USER_ID')):
            
            # For GET requests in preview, skip CSRF entirely
            if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
                return None
                
            # For POST requests, try to be more lenient
            # Log the issue but don't block the request in development
            if settings.DEBUG:
                logger.info(f"Replit preview environment detected - being lenient with CSRF for {request.path}")
        
        # Use the parent's normal processing
        return super().process_view(request, callback, callback_args, callback_kwargs)


class ReplitHeadersMiddleware:
    """
    Middleware to add headers that help with Replit preview environment compatibility.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add headers to help with iframe embedding in Replit preview
        response['X-Frame-Options'] = 'ALLOWALL'  # Allow embedding in Replit
        response['Content-Security-Policy'] = "frame-ancestors 'self' *.replit.app *.repl.co"
        
        # Ensure cookies work in iframe context
        if hasattr(response, 'cookies'):
            for cookie in response.cookies.values():
                cookie['samesite'] = 'Lax'
        
        return response