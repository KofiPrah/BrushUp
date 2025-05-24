"""
Update the workflow to use HTTP-only mode
"""
import json
import os

def main():
    workflow_data = {
        "name": "Start application",
        "command": "python flask_proxy.py"
    }
    
    with open('http_workflow.json', 'w') as f:
        json.dump(workflow_data, f, indent=2)
    
    print("Workflow updated to use HTTP proxy")

if __name__ == "__main__":
    main()