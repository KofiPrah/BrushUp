"""
Django management command to enable WebSocket support for real-time notifications.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Enable WebSocket support for real-time notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--disable',
            action='store_true',
            help='Disable WebSocket support instead of enabling it',
        )

    def handle(self, *args, **options):
        settings_file = os.path.join(settings.BASE_DIR, 'artcritique', 'settings.py')
        
        if options['disable']:
            # Disable WebSocket support
            self.disable_websockets(settings_file)
        else:
            # Enable WebSocket support
            self.enable_websockets(settings_file)

    def enable_websockets(self, settings_file):
        """Enable WebSocket support in settings."""
        with open(settings_file, 'r') as f:
            content = f.read()

        # Enable ASGI application
        content = content.replace(
            "# ASGI_APPLICATION = 'artcritique.asgi.application'  # Temporarily disabled for WSGI compatibility",
            "ASGI_APPLICATION = 'artcritique.asgi.application'"
        )

        with open(settings_file, 'w') as f:
            f.write(content)

        self.stdout.write(
            self.style.SUCCESS(
                "✅ WebSocket support enabled!\n"
                "🔄 Please restart the server for changes to take effect.\n"
                "📡 Real-time notifications will be available at: ws://your-domain/ws/notifications/"
            )
        )

    def disable_websockets(self, settings_file):
        """Disable WebSocket support in settings."""
        with open(settings_file, 'r') as f:
            content = f.read()

        # Disable ASGI application
        content = content.replace(
            "ASGI_APPLICATION = 'artcritique.asgi.application'",
            "# ASGI_APPLICATION = 'artcritique.asgi.application'  # Temporarily disabled for WSGI compatibility"
        )

        with open(settings_file, 'w') as f:
            f.write(content)

        self.stdout.write(
            self.style.WARNING(
                "⚠️ WebSocket support disabled.\n"
                "🔄 Please restart the server for changes to take effect.\n"
                "📱 Notifications will fall back to polling mode."
            )
        )