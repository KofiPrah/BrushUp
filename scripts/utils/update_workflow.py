#!/usr/bin/env python3
"""
Script to update the workflow configuration to HTTP mode.
This creates a backup of the current workflow and updates
the start command to use HTTP mode.
"""
import os
import json
import datetime

# Constants
CONFIG_FILE = ".replit"
BACKUP_TEMPLATE = "{}.backup.{}"


def backup_config(config_path):
    """Create a backup of the config file"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = BACKUP_TEMPLATE.format(config_path, timestamp)
    try:
        with open(config_path, "r") as src, open(backup_path, "w") as dest:
            dest.write(src.read())
        print(f"Backed up {config_path} to {backup_path}")
        return True
    except Exception as e:
        print(f"Error backing up config: {e}")
        return False


def create_http_config(config_path):
    """Create a new configuration file for HTTP mode"""
    http_config = """modules = ["python-3.11", "postgresql-16", "nodejs-20"]

[nix]
channel = "stable-24_05"
packages = ["awscli2", "cargo", "freetype", "jre17_minimal", "lcms2", "libiconv", "libimagequant", "libjpeg", "libtiff", "libwebp", "libxcrypt", "openjpeg", "openssl", "pkg-config", "postgresql", "rustc", "tcl", "tk", "zlib"]

[deployment]
deploymentTarget = "autoscale"
run = ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]

[workflows]
runButton = "Project"

[[workflows.workflow]]
name = "Project"
mode = "parallel"
author = "agent"

[[workflows.workflow.tasks]]
task = "workflow.run"
args = "Start application"

[[workflows.workflow]]
name = "Start application"
author = "agent"

[[workflows.workflow.tasks]]
task = "shell.exec"
args = "./run_http.sh"
waitForPort = 5000

[[ports]]
localPort = 5000
externalPort = 80

[[ports]]
localPort = 8000
externalPort = 8000

[[ports]]
localPort = 8080
externalPort = 8080

[env]
SSL_ENABLED = "false"
HTTP_ONLY = "true"
"""
    try:
        with open(config_path + ".new", "w") as f:
            f.write(http_config)
        print(f"Created new HTTP configuration at {config_path}.new")
        print("Instructions:")
        print("1. Copy the content of the new file to .replit")
        print("2. Restart the Replit server")
        return True
    except Exception as e:
        print(f"Error creating HTTP config: {e}")
        return False


def main():
    """Main function to update workflow configuration"""
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found")
        return False

    # Create a backup first
    if not backup_config(CONFIG_FILE):
        print("Backup failed, aborting update")
        return False
    
    # Create the new HTTP config file
    if not create_http_config(CONFIG_FILE):
        print("Failed to create HTTP config")
        return False
    
    print("\nWorkflow configuration updated successfully!")
    print(f"Please manually update {CONFIG_FILE} with the content from {CONFIG_FILE}.new")
    print("Then restart your Repl to apply the changes.")
    return True


if __name__ == "__main__":
    main()