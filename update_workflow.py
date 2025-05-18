#!/usr/bin/env python3
"""
Create and update workflow configuration for HTTP-only mode
"""
import json
import os
import subprocess

def create_workflow_file():
    """Create a JSON file to help update the workflow configuration"""
    workflow_config = {
        "name": "HTTP Only Server",
        "author": "agent",
        "tasks": [
            {
                "task": "shell.exec",
                "args": "./start_http.sh",
                "waitForPort": 5000
            }
        ]
    }
    
    with open("http_workflow.json", "w") as f:
        json.dump(workflow_config, f, indent=4)
    
    print("Created workflow configuration file: http_workflow.json")
    print("To use this workflow:")
    print("1. Go to Tools > Workflow Config")
    print("2. Create a new workflow named 'HTTP Only Server'")
    print("3. Configure with command: ./start_http.sh")
    print("4. Click run to start the HTTP-only server")

if __name__ == "__main__":
    create_workflow_file()