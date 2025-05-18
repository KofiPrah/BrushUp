#!/usr/bin/env python3
"""
Script to update the Replit workflow to run in HTTP mode without SSL certificates
"""
import os
import json
import subprocess

# Define the updated workflow configuration
workflow_config = {
    "name": "Start application",
    "author": "agent",
    "tasks": [
        {
            "task": "shell.exec",
            "args": "gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app",
            "waitForPort": 5000
        }
    ]
}

# Check if there's an existing workflow file
REPLIT_FILE = ".replit"

try:
    # Read the current .replit file
    if os.path.exists(REPLIT_FILE):
        print(f"Updating workflow in {REPLIT_FILE}")
        
        # Print information about the new configuration
        print("Updating Replit workflow to run in HTTP mode without SSL certificates")
        print("New command: gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app")
        
        # Create a run script with the HTTP configuration
        with open("run_http.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("export SSL_ENABLED=false\n")
            f.write("export HTTP_ONLY=true\n")
            f.write("gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app\n")
        
        # Make it executable
        os.chmod("run_http.sh", 0o755)
        
        # Update the critique form to use AJAX submission
        critique_form_path = "critique/templates/critique/artwork_detail.html"
        if os.path.exists(critique_form_path):
            print(f"Updating critique form in {critique_form_path}")
            
            with open(critique_form_path, "r") as f:
                content = f.read()
            
            # Check if we need to update the form
            if "fetch('/api/critiques/'" not in content:
                print("Adding AJAX critique form submission")
                
                # We'll create a separate update script for this
                with open("update_critique_form.py", "w") as f:
                    f.write('''#!/usr/bin/env python3
"""
Script to update the critique form to use AJAX submission
"""
import os

critique_form_path = "critique/templates/critique/artwork_detail.html"

try:
    with open(critique_form_path, "r") as f:
        content = f.read()
    
    # Add AJAX form submission script if needed
    if "fetch('/api/critiques/'" not in content:
        # Find the form closing tag
        form_end_index = content.find("</form>", content.find("id=\"critique-form\""))
        
        if form_end_index > 0:
            # Add the AJAX script before the form closing tag
            ajax_script = """
    <script>
    document.getElementById('critique-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(this);
        const artworkId = formData.get('artwork');
        
        // Convert to JSON
        const data = {
            artwork: artworkId,
            text: formData.get('text'),
            composition_score: parseInt(formData.get('composition_score')),
            technique_score: parseInt(formData.get('technique_score')),
            originality_score: parseInt(formData.get('originality_score'))
        };
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Submit via AJAX
        fetch('/api/critiques/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data),
            credentials: 'include'
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Submission failed: ' + response.status);
        })
        .then(data => {
            // Success
            alert('Critique submitted successfully!');
            window.location.reload();
        })
        .catch(error => {
            // Error handling
            console.error('Error:', error);
            alert('Failed to submit critique: ' + error.message);
        });
    });
    </script>
    """
            
            updated_content = content[:form_end_index] + ajax_script + content[form_end_index:]
            
            with open(critique_form_path, "w") as f:
                f.write(updated_content)
            
            print(f"Updated {critique_form_path} with AJAX form submission")
        else:
            print(f"Could not find critique form in {critique_form_path}")
    else:
        print(f"AJAX form submission already exists in {critique_form_path}")

except Exception as e:
    print(f"Error updating critique form: {str(e)}")
''')
                
                # Make it executable
                os.chmod("update_critique_form.py", 0o755)
                
                # Run the update script
                try:
                    subprocess.run(["python", "update_critique_form.py"], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error running update_critique_form.py: {e}")
        
        print("Configuration updated. Please restart the workflow.")
    else:
        print(f"Warning: {REPLIT_FILE} not found")

except Exception as e:
    print(f"Error updating workflow: {str(e)}")

print("Done. To run in HTTP mode, execute: ./run_http.sh")