#!/usr/bin/env python3
"""
Fix specific JavaScript template literal issues that broke functionality
"""

import re

def fix_artwork_detail():
    """Fix broken JavaScript in artwork_detail.html"""
    with open('critique/templates/critique/artwork_detail.html', 'r') as f:
        content = f.read()
    
    # Fix broken template literal selectors
    content = re.sub(
        r'document\.querySelector\(`\[data-version="' + r"' \+ versionId \+ '" + r'"\]`\)',
        r'document.querySelector(`[data-version="${versionId}"]`)',
        content
    )
    
    # Fix broken fetch URLs
    content = re.sub(
        r'fetch\(`/api/artworks/' + r"' \+ artworkId \+ '" + r'/versions/' + r"' \+ versionId \+ '" + r'/`',
        r'fetch(`/api/artworks/${artworkId}/versions/${versionId}/`',
        content
    )
    
    # Fix other broken template literals in JavaScript
    content = re.sub(
        r'`([^`]*?)' + r"' \+ ([^']+) \+ '" + r'([^`]*?)`',
        r'`\1${\2}\3`',
        content
    )
    
    with open('critique/templates/critique/artwork_detail.html', 'w') as f:
        f.write(content)
    
    print("Fixed artwork_detail.html JavaScript")

def fix_profile():
    """Fix broken JavaScript in profile.html"""
    with open('critique/templates/critique/profile.html', 'r') as f:
        content = f.read()
    
    # Fix any similar broken template literals in profile
    content = re.sub(
        r'`([^`]*?)' + r"' \+ ([^']+) \+ '" + r'([^`]*?)`',
        r'`\1${\2}\3`',
        content
    )
    
    with open('critique/templates/critique/profile.html', 'w') as f:
        f.write(content)
    
    print("Fixed profile.html JavaScript")

if __name__ == "__main__":
    fix_artwork_detail()
    fix_profile()
    print("JavaScript template literal fixes complete")