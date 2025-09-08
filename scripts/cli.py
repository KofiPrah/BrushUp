#!/usr/bin/env python3
"""Unified command line interface for BrushUp deployment.

This script consolidates the various start/run helpers into a single
interface.  It provides flags for selecting the protocol, enabling SSL
and running pre‑launch workflow steps that previous helper scripts
performed.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

CERT_DIR = Path('certs')


def _ensure_disabled_ssl():
    """Rename existing cert files and create empty placeholders."""
    CERT_DIR.mkdir(exist_ok=True)
    for name in ("cert.pem", "key.pem"):
        path = CERT_DIR / name
        disabled = path.with_suffix(path.suffix + ".disabled")
        if path.exists() and not disabled.exists():
            path.rename(disabled)
        # create empty file so other tooling doesn't fail looking for it
        path.touch()


def serve(args: argparse.Namespace) -> None:
    """Start the application server according to CLI options."""
    env = os.environ.copy()
    port = str(args.port)

    if args.protocol == "http":
        env["HTTPS"] = "off"
        env["wsgi.url_scheme"] = "http"

    if not args.ssl:
        _ensure_disabled_ssl()

    # optional workflow pre-steps
    script_dir = Path(__file__).resolve().parent
    if args.workflow:
        subprocess.run([sys.executable, str(script_dir / "fix_karma_db.py")], check=False)
        subprocess.run([sys.executable, str(script_dir / "fix_critique_serializer.py")], check=False)

    if args.server == "django":
        env.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
        cmd = [sys.executable, "manage.py", "runserver", f"0.0.0.0:{port}"]
    elif args.server == "gunicorn":
        app = args.app or "artcritique.wsgi:application"
        cmd = [
            "gunicorn",
            "--bind", f"0.0.0.0:{port}",
            "--reload",
            app,
        ]
        if args.protocol == "https" and args.ssl:
            cmd.extend([
                "--certfile",
                str(CERT_DIR / "cert.pem"),
                "--keyfile",
                str(CERT_DIR / "key.pem"),
            ])
    else:  # daphne for ASGI/websockets
        app = args.app or "artcritique.asgi:application"
        cmd = [
            "daphne",
            "-b", "0.0.0.0",
            "-p", port,
            app,
        ]

    subprocess.run(cmd, env=env)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="BrushUp deployment helper")
    sub = parser.add_subparsers(dest="command")

    serve_parser = sub.add_parser("serve", help="Start application server")
    serve_parser.add_argument(
        "--protocol", choices=["http", "https"], default="http",
        help="Protocol to expose."
    )
    serve_parser.add_argument(
        "--ssl", action="store_true", help="Enable SSL certificates"
    )
    serve_parser.add_argument(
        "--server", choices=["django", "gunicorn", "daphne"], default="django",
        help="Underlying server implementation."
    )
    serve_parser.add_argument(
        "--port", type=int, default=5000, help="Port to bind"
    )
    serve_parser.add_argument(
        "--app", help="WSGI/ASGI application path for gunicorn/daphne"
    )
    serve_parser.add_argument(
        "--workflow", action="store_true", help="Run pre-launch workflow fixes"
    )
    serve_parser.set_defaults(func=serve)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
