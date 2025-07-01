"""
Management command to create default achievement badges.
Run with: python manage.py create_default_badges
"""

from django.core.management.base import BaseCommand
from critique.services import create_default_badges


class Command(BaseCommand):
    help = 'Creates default achievement badges for the platform'

    def handle(self, *args, **options):
        self.stdout.write('Creating default achievement badges...')
        
        created_count = create_default_badges()
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} new badges')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No new badges were created (they may already exist)')
            )