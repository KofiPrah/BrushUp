import re
import glob

def fix_template_literals(content):
    """Fix JavaScript template literals in HTML content"""
    # Replace template literals with string concatenation
    patterns = [
        # Simple ${variable} replacements
        (r'\$\{([^}]+)\}', r"' + \1 + '"),
        
        # Fix specific problematic patterns
        (r'`([^`]*toast bg-)\$\{([^}]+)\}([^`]*)`', r"'\1' + \2 + '\3'"),
        (r'`([^`]*)\$\{([^}]+)\}([^`]*)`', r"'\1' + \2 + '\3'"),
        
        # Clean up extra concatenations
        (r"' \+ '' \+ '", r"'"),
        (r"'' \+ '", r"'"),
        (r"' \+ ''", r"'"),
        (r"' \+ ' \+ '", r"' + '"),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

# Process all HTML template files
files = glob.glob('critique/templates/**/*.html', recursive=True)
fixed_files = []

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    fixed_content = fix_template_literals(original_content)
    
    if fixed_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        fixed_files.append(filepath)

print(f"Fixed template literals in {len(fixed_files)} files:")
for f in fixed_files:
    print(f"  - {f}")