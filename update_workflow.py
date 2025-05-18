#!/usr/bin/env python3
"""
Update the workflow to use HTTP-only mode without SSL
for compatibility with Replit's environment
"""
import os
import json

# Define the updated workflow configuration
workflow_content = {
    "modules": ["python-3.11", "postgresql-16", "nodejs-20"],
    "nix": {
        "channel": "stable-24_05",
        "packages": ["awscli2", "cargo", "freetype", "jre17_minimal", "lcms2", "libiconv", "libimagequant", "libjpeg", "libtiff", "libwebp", "libxcrypt", "openjpeg", "openssl", "pkg-config", "postgresql", "rustc", "tcl", "tk", "zlib"]
    },
    "deployment": {
        "deploymentTarget": "autoscale",
        "run": ["python", "http_server_nossl.py"]
    },
    "workflows": {
        "runButton": "Project",
        "workflow": [
            {
                "name": "Project",
                "mode": "parallel",
                "author": "agent",
                "tasks": [
                    {
                        "task": "workflow.run",
                        "args": "Start application"
                    }
                ]
            },
            {
                "name": "Start application",
                "author": "agent",
                "tasks": [
                    {
                        "task": "shell.exec",
                        "args": "python http_server_nossl.py",
                        "waitForPort": 5000
                    }
                ]
            }
        ]
    },
    "ports": [
        {
            "localPort": 5000,
            "externalPort": 80
        },
        {
            "localPort": 8000,
            "externalPort": 8000
        },
        {
            "localPort": 8080,
            "externalPort": 8080
        }
    ],
    "env": {
        "SSL_ENABLED": "false",
        "HTTP_ONLY": "true"
    }
}

print("Attempting to update .replit.new file...")
with open('.replit.new', 'w') as f:
    json.dump(workflow_content, f, indent=2)
print("Successfully created .replit.new with HTTP-only configuration")

print("\nTo enable HTTP mode:")
print("1. Replace the .replit file with .replit.new")
print("2. Restart Replit")
print("3. Alternatively, manually update the workflow to use 'python http_server_nossl.py'")