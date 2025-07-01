#!/usr/bin/env python3
"""
Add Focus Mode to artwork detail template
"""

import re

def add_focus_mode():
    """Add Focus Mode HTML structure to artwork detail template"""
    
    # Read the template file
    with open('critique/templates/critique/artwork_detail.html', 'r') as f:
        content = f.read()
    
    # Find where to insert Focus Mode (after {% endblock %} of extra_head)
    pattern = r'(</style>\s*{% endblock %})'
    
    focus_mode_html = '''</style>
{% endblock %}

{% block content %}

<!-- Focus Mode Section -->
<section id="focus-mode">
    <img id="focus-artwork" 
         src="{% if current_version and current_version.image %}{{ current_version.image.url }}{% elif current_version and current_version.image_url %}{{ current_version.image_url }}{% elif artwork.image %}{{ artwork.image.url }}{% elif artwork.image_url %}{{ artwork.image_url }}{% endif %}" 
         alt="{{ artwork.title }}" 
         onclick="enterFullscreen(this)">
    
    <!-- Delayed UI Elements -->
    <div id="delayed-ui">
        <button class="favorite-btn focus-ui-element" onclick="toggleFavorite({{ artwork.id }})" title="Add to Favorites">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16">
                <path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/>
            </svg>
        </button>
        
        <div class="version-chip">
            v{{ current_version_number|default:"1" }} (Current)
        </div>
        
        <a href="#scroll-anchor" class="focus-ui-element" onclick="exitFocusMode()">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chat-left-text me-2" viewBox="0 0 16 16">
                <path d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4.414A2 2 0 0 0 3 11.586l-2 2V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12.793a.5.5 0 0 0 .854.353l2.853-2.853A1 1 0 0 1 4.414 12H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
                <path d="M3 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM3 6a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 6zm0 2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5z"/>
            </svg>
            See Critiques
        </a>
        
        <a href="{% url 'critique:create_critique' artwork.id %}" class="focus-ui-element btn-add-critique">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-circle me-2" viewBox="0 0 16 16">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>
            Add Critique
        </a>
    </div>
    
    <!-- Scroll Indicator -->
    <div class="scroll-indicator" onclick="exitFocusMode()">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>
        </svg>
    </div>
</section>

<!-- Main Content (Initially Hidden) -->
<div id="main-content">
    <div id="scroll-anchor"></div>'''
    
    # Replace the pattern
    if re.search(pattern, content):
        content = re.sub(pattern, focus_mode_html, content, count=1)
        
        # Wrap existing container-fluid with main-content div
        content = content.replace('<div class="container-fluid py-4">', '<div class="container-fluid py-4">')
        
        # Add closing div for main-content at the end (before {% endblock content %})
        content = content.replace('{% endblock content %}', '</div>\n{% endblock content %}')
        
        # Write back to file
        with open('critique/templates/critique/artwork_detail.html', 'w') as f:
            f.write(content)
            
        print("✓ Focus Mode HTML structure added successfully")
    else:
        print("✗ Could not find insertion point for Focus Mode")

if __name__ == "__main__":
    add_focus_mode()