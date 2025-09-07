"""
Update the workflow to use the unified CLI
"""
import json

def main():
    workflow_data = {
        "name": "Start application",
        "command": "python scripts/cli.py serve --protocol http"
    }
    with open('http_workflow.json', 'w') as f:
        json.dump(workflow_data, f, indent=2)
    print("Workflow updated to use unified CLI")

if __name__ == "__main__":
    main()
