from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Sets up the default Site model for django-allauth'

    def handle(self, *args, **options):
        # Update or create the default site
        site, created = Site.objects.update_or_create(
            id=1,
            defaults={
                'domain': 'artcritique.replit.app',
                'name': 'Art Critique'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Site model'))
        else:
            self.stdout.write(self.style.SUCCESS('Successfully updated Site model'))