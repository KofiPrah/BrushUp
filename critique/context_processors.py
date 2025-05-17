from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sessions.models import Session
from django.utils import timezone
from critique.models import KarmaEvent, Notification

def site_info(request):
    """
    Context processor to add site-related information to the context
    for all templates.
    """
    current_site = get_current_site(request)
    return {
        'site': current_site,
        'site_name': current_site.name,
        'site_domain': current_site.domain,
    }

def karma_notifications(request):
    """
    Context processor to add recent karma notifications to the context
    for all templates.
    """
    context = {}
    
    # Only show karma notifications for authenticated users
    if request.user.is_authenticated:
        # Check if there's a recent karma event that hasn't been seen yet
        # Use session to track which karma events have been shown
        session_key = f"shown_karma_event_{request.user.id}"
        last_shown_id = request.session.get(session_key, 0)
        
        # Get the most recent karma event that hasn't been shown yet
        recent_event = KarmaEvent.objects.filter(
            user=request.user, 
            id__gt=last_shown_id
        ).order_by('-created_at').first()
        
        if recent_event:
            # Store this event as shown
            request.session[session_key] = recent_event.id
            
            # Prepare notification for the template
            context['karma_notification'] = {
                'points': recent_event.points,
                'reason': recent_event.reason or f"for {recent_event.action}"
            }
            
            # Create a notification for the user if it doesn't exist yet
            Notification.objects.get_or_create(
                recipient=request.user,
                message=f"You earned {recent_event.points} karma points for {recent_event.action}",
                defaults={
                    'url': '/profile/',
                    'is_read': False
                }
            )
    
    return context