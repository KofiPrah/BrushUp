#!/usr/bin/env python3
"""
Add Focus Mode JavaScript to artwork detail template
"""

def add_focus_mode_js():
    """Add Focus Mode JavaScript functionality"""
    
    # Read the template file
    with open('critique/templates/critique/artwork_detail.html', 'r') as f:
        content = f.read()
    
    # Focus Mode JavaScript to add
    focus_js = '''
    // Focus Mode Functions
    function enterFullscreen(img) {
        if (img.requestFullscreen) {
            img.requestFullscreen();
        } else if (img.webkitRequestFullscreen) {
            img.webkitRequestFullscreen();
        } else if (img.msRequestFullscreen) {
            img.msRequestFullscreen();
        }
    }
    
    function exitFocusMode() {
        const mainContent = document.getElementById('main-content');
        const focusMode = document.getElementById('focus-mode');
        
        // Hide focus mode
        focusMode.style.display = 'none';
        
        // Show main content with animation
        mainContent.classList.add('visible');
        
        // Smooth scroll to anchor
        document.getElementById('scroll-anchor').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
    
    function toggleFavorite(artworkId) {
        // Implement favorite functionality here
        const btn = event.target.closest('.favorite-btn');
        const heart = btn.querySelector('svg');
        
        // Toggle visual state
        if (heart.classList.contains('bi-heart')) {
            heart.classList.remove('bi-heart');
            heart.classList.add('bi-heart-fill');
            btn.style.background = 'rgba(220,53,69,0.3)';
            btn.style.color = '#dc3545';
        } else {
            heart.classList.remove('bi-heart-fill');
            heart.classList.add('bi-heart');
            btn.style.background = 'rgba(220,53,69,0.15)';
        }
        
        // Add API call here when ready
        console.log('Toggling favorite for artwork:', artworkId);
    }'''
    
    # Add before the last DOMContentLoaded function
    pattern = r'(document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{[^}]+?\}\);)'
    
    if pattern in content:
        # Find the last DOMContentLoaded function and add Focus Mode functions before it
        last_dom_ready = content.rfind("document.addEventListener('DOMContentLoaded'")
        if last_dom_ready != -1:
            # Insert Focus Mode functions before the last DOMContentLoaded
            content = content[:last_dom_ready] + focus_js + '\n\n    ' + content[last_dom_ready:]
            
            # Also add auto-transition logic to the DOMContentLoaded
            auto_transition_code = '''
        // Focus Mode auto-transition after delay
        setTimeout(() => {
            const mainContent = document.getElementById('main-content');
            if (!mainContent.classList.contains('visible')) {
                // Auto-transition after 8 seconds if user doesn't interact
                setTimeout(exitFocusMode, 8000);
            }
        }, 2000);'''
            
            # Add to the end of the DOMContentLoaded function (before the closing brace)
            dom_ready_end = content.find('});', last_dom_ready)
            if dom_ready_end != -1:
                content = content[:dom_ready_end] + auto_transition_code + '\n    ' + content[dom_ready_end:]
        
        # Write back to file
        with open('critique/templates/critique/artwork_detail.html', 'w') as f:
            f.write(content)
            
        print("✓ Focus Mode JavaScript functions added successfully")
    else:
        print("✗ Could not find DOMContentLoaded function to modify")

if __name__ == "__main__":
    add_focus_mode_js()