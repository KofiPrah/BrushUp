#!/usr/bin/env python3
"""
Script to fix JavaScript template literals in HTML templates that are causing broken HTML
"""

import os
import re
import glob

def fix_template_literals_in_file(filepath):
    """Fix template literals in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match template literals with ${...} expressions
    template_literal_patterns = [
        # Simple ${variable} patterns
        (r'\$\{([^}]+)\}', r'" + \1 + "'),
        
        # Fix backtick template literals to string concatenation
        (r'`([^`]*\$\{[^`]*)`', lambda m: convert_template_literal(m.group(1))),
    ]
    
    # Apply fixes
    for pattern, replacement in template_literal_patterns:
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed template literals in: {filepath}")
        return True
    return False

def convert_template_literal(template_str):
    """Convert a template literal string to concatenation"""
    # Simple conversion - replace ${var} with " + var + "
    result = template_str
    result = re.sub(r'\$\{([^}]+)\}', r'" + \1 + "', result)
    
    # Clean up extra quotes and concatenation
    result = result.replace('+ ""', '').replace('"" + ', '')
    result = result.strip('"')
    
    return f'"{result}"'

def main():
    """Main function to fix all template files"""
    template_files = glob.glob('critique/templates/**/*.html', recursive=True)
    
    fixed_count = 0
    for filepath in template_files:
        if fix_template_literals_in_file(filepath):
            fixed_count += 1
    
    print(f"Fixed template literals in {fixed_count} files")

if __name__ == "__main__":
    main()