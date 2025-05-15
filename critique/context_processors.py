from django.contrib.sites.shortcuts import get_current_site

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