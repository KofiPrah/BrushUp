#!/usr/bin/env python3
"""
Fix all remaining template literal issues causing broken HTML
"""

import re

def fix_artwork_detail():
    """Fix all remaining template literal issues in artwork_detail.html"""
    with open('critique/templates/critique/artwork_detail.html', 'r') as f:
        content = f.read()
    
    # Fix specific broken patterns
    fixes = [
        # Fix Error template literals
        (r'throw new Error\(`Error: \$\{response\.status\} - \' \+ text \+ \'\`\);', 
         r'throw new Error(`Error: ${response.status} - ${text}`);'),
        
        # Fix version preview selectors
        (r'document\.getElementById\(`versionPreview\' \+ selectorNum \+ \'\`\)', 
         r'document.getElementById(`versionPreview${selectorNum}`);'),
        
        # Fix version deletion modals
        (r'<p>Are you sure you want to delete <strong>Version \' \+ versionNumber \+ \'</strong>\?</p>',
         r'<p>Are you sure you want to delete <strong>Version ${versionNumber}</strong>?</p>'),
        
        (r'onclick="confirmDeleteVersion\(\' \+ versionId \+ \'\)"',
         r'onclick="confirmDeleteVersion(${versionId})"'),
        
        # Fix HTTP error messages
        (r'throw new Error\(`HTTP \$\{response\.status\}: \' \+ response\.statusText \+ \'\`\);',
         r'throw new Error(`HTTP ${response.status}: ${response.statusText}`);'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    with open('critique/templates/critique/artwork_detail.html', 'w') as f:
        f.write(content)
    
    print("Fixed remaining template literal issues in artwork_detail.html")

if __name__ == "__main__":
    fix_artwork_detail()