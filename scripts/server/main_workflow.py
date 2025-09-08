#!/usr/bin/env python3
"""HTTP-only main file for workflow use."""
from pathlib import Path
import subprocess

# Run our HTTP-only startup script relative to repository root
run_script = Path(__file__).resolve().parent.parent / "run.sh"
subprocess.run([str(run_script)])
