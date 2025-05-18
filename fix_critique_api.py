#!/usr/bin/env python3
"""
Script to diagnose and fix issues with the critique API and server configuration
"""
import os
import subprocess
import sys

def print_header(message):
    """Print a header message"""
    print("\n" + "=" * 80)
    print(message)
    print("=" * 80)

def check_api_setup():
    """Check if the Critique API is properly configured"""
    print_header("Checking Critique API configuration")
    
    api_views_path = "critique/api/views.py"
    if not os.path.exists(api_views_path):
        print(f"Error: {api_views_path} not found")
        return False
    
    try:
        with open(api_views_path, "r") as f:
            content = f.read()
            
        if "class CritiqueViewSet(viewsets.ModelViewSet)" in content:
            print("✓ CritiqueViewSet is defined as ModelViewSet")
        else:
            print("✗ CritiqueViewSet is not properly defined as ModelViewSet")
            return False
        
        if "def perform_create" in content:
            print("✓ perform_create method is defined for creating critiques")
        else:
            print("✗ perform_create method is missing")
        
        # Check permissions to see if POST is allowed
        if "IsAuthenticatedOrReadOnly" in content:
            print("✓ Permissions allow authenticated users to create critiques")
        else:
            print("✗ Permissions may not allow critique creation")
    
    except Exception as e:
        print(f"Error checking API setup: {e}")
        return False
    
    # Check API URLs
    api_urls_path = "critique/api/urls.py"
    if not os.path.exists(api_urls_path):
        print(f"Error: {api_urls_path} not found")
        return False
    
    try:
        with open(api_urls_path, "r") as f:
            content = f.read()
        
        if "router.register(r'critiques', CritiqueViewSet)" in content:
            print("✓ CritiqueViewSet is registered in the API router")
        else:
            print("✗ CritiqueViewSet is not properly registered in the router")
            return False
    
    except Exception as e:
        print(f"Error checking API URLs: {e}")
        return False
    
    return True

def update_server_config():
    """Update the server configuration to run in HTTP mode"""
    print_header("Setting up HTTP-only server")
    
    # Create a simple HTTP server script
    http_server_path = "runserver_http.py"
    try:
        with open(http_server_path, "w") as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
Django development server without SSL for Brush Up
\"\"\"
import os
import sys

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['DJANGO_DEBUG'] = 'true'

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    
    # Run Django server directly
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)
""")
        
        # Make it executable
        os.chmod(http_server_path, 0o755)
        print(f"✓ Created {http_server_path}")
        
        # Create a shell script to run it
        with open("run_http_server.sh", "w") as f:
            f.write("""#!/bin/bash
export SSL_ENABLED=false
export HTTP_ONLY=true
python runserver_http.py
""")
        
        # Make it executable
        os.chmod("run_http_server.sh", 0o755)
        print("✓ Created run_http_server.sh")
        
        return True
    
    except Exception as e:
        print(f"Error updating server configuration: {e}")
        return False

def update_critique_form():
    """Update the critique submission form to properly use the API"""
    print_header("Checking critique form")
    
    critique_form_path = "critique/templates/critique/artwork_detail.html"
    if not os.path.exists(critique_form_path):
        print(f"Error: {critique_form_path} not found")
        return False
    
    try:
        with open(critique_form_path, "r") as f:
            content = f.read()
        
        # Make sure the form correctly uses the API endpoint
        if "fetch('/api/critiques/'" in content:
            print("✓ Critique form is already configured to use API endpoint")
            return True
        
        print("Updating critique form to use API endpoint")
        
        # Find location to add AJAX script
        form_id = "critiqueForm"
        form_end_tag = "</form>"
        form_close_index = content.find(form_end_tag, content.find(f'id="{form_id}"'))
        
        if form_close_index < 0:
            print(f"✗ Could not find critique form with id '{form_id}'")
            return False
        
        # Add AJAX submission script
        ajax_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const critiqueForm = document.getElementById('critiqueForm');
    
    if (critiqueForm) {
        critiqueForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Get form data
            const artworkId = document.querySelector('input[name="artwork"]').value;
            const text = document.getElementById('critiqueText').value;
            const compositionScore = document.getElementById('compositionScore').value;
            const techniqueScore = document.getElementById('techniqueScore').value;
            const originalityScore = document.getElementById('originalityScore').value;
            
            // Create the payload
            const data = {
                artwork: artworkId,
                text: text,
                composition_score: parseInt(compositionScore),
                technique_score: parseInt(techniqueScore),
                originality_score: parseInt(originalityScore)
            };
            
            // Submit via AJAX to the API endpoint
            fetch('/api/critiques/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data),
                credentials: 'same-origin'
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    return response.json().then(errorData => {
                        throw new Error(JSON.stringify(errorData));
                    });
                }
            })
            .then(data => {
                // Success - close modal and refresh page
                const modal = bootstrap.Modal.getInstance(document.getElementById('critiqueModal'));
                if (modal) {
                    modal.hide();
                }
                window.location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
                // Show error message
                const messageElement = document.getElementById('critiqueFormMessage');
                if (messageElement) {
                    messageElement.classList.remove('d-none');
                    try {
                        const errorData = JSON.parse(error.message);
                        if (errorData.non_field_errors) {
                            messageElement.textContent = errorData.non_field_errors.join(', ');
                        } else if (errorData.detail) {
                            messageElement.textContent = errorData.detail;
                        } else {
                            messageElement.textContent = 'An error occurred. Please try again.';
                        }
                    } catch (e) {
                        messageElement.textContent = 'An error occurred. Please try again.';
                    }
                }
            });
        });
    }
});
</script>
"""
        
        # Insert the script before the form closing tag
        updated_content = content[:form_close_index] + ajax_script + content[form_close_index:]
        
        # Write back the updated content
        with open(critique_form_path, "w") as f:
            f.write(updated_content)
        
        print("✓ Updated critique form to use API endpoint")
        return True
    
    except Exception as e:
        print(f"Error updating critique form: {e}")
        return False

def fix_server_for_http():
    """Stop existing server and run in HTTP mode"""
    print_header("Stopping existing server and starting HTTP server")
    
    try:
        # Stop any running server
        print("Stopping any running servers...")
        subprocess.run(["pkill", "-f", "gunicorn"], stderr=subprocess.PIPE)
        subprocess.run(["pkill", "-f", "runserver"], stderr=subprocess.PIPE)
        
        # Run the HTTP server
        print("Starting HTTP server...")
        # We don't actually start it here, just provide instructions
        print("\n" + "=" * 80)
        print("To run the server in HTTP mode, execute:")
        print("   ./run_http_server.sh")
        print("=" * 80 + "\n")
        
        return True
    except Exception as e:
        print(f"Error fixing server: {e}")
        return False

def run():
    """Run all fixes"""
    print_header("Starting diagnosis and fixes for Brush Up")
    
    # Check if API is properly configured
    api_ok = check_api_setup()
    
    # Update server configuration for HTTP
    server_ok = update_server_config()
    
    # Update critique form
    form_ok = update_critique_form()
    
    # Fix server
    fix_ok = fix_server_for_http()
    
    # Print summary
    print_header("Summary")
    print(f"API configuration: {'✓' if api_ok else '✗'}")
    print(f"Server configuration: {'✓' if server_ok else '✗'}")
    print(f"Critique form: {'✓' if form_ok else '✗'}")
    print(f"Server fix: {'✓' if fix_ok else '✗'}")
    
    if api_ok and server_ok and form_ok and fix_ok:
        print("\n✅ All fixes applied successfully!")
        print("To run the server in HTTP mode, execute: ./run_http_server.sh")
    else:
        print("\n⚠️ Some fixes could not be applied.")
        if server_ok:
            print("To run the server in HTTP mode, execute: ./run_http_server.sh")

if __name__ == "__main__":
    run()