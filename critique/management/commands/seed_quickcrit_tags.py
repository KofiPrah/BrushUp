"""
Management command to seed the database with initial critique tags
for the two-at-a-time critique feed system.
"""

from django.core.management.base import BaseCommand
from critique.models import Tag


class Command(BaseCommand):
    help = 'Seed the database with initial critique tags for the quick critique system'

    def handle(self, *args, **kwargs):
        """Create initial system tags for the critique feed."""
        
        # Define seed tags organized by category and polarity
        SEED_TAGS = {
            "PRO": {
                "composition": [
                    "strong focal point", "balanced layout", "clear silhouette", 
                    "dynamic perspective", "effective framing", "good use of space",
                    "strong visual hierarchy", "compelling composition"
                ],
                "technique": [
                    "confident brushwork", "clean linework", "color harmony", 
                    "skillful rendering", "masterful technique", "precise execution",
                    "excellent craftsmanship", "strong fundamentals"
                ],
                "concept": [
                    "compelling concept", "evocative mood", "original idea", 
                    "clear narrative", "powerful symbolism", "creative vision",
                    "thought-provoking", "emotionally resonant"
                ],
                "style": [
                    "distinctive style", "cohesive aesthetic", "unique voice",
                    "artistic maturity", "personal expression"
                ]
            },
            "CON": {
                "composition": [
                    "muddy values", "tangent issues", "awkward cropping", 
                    "weak focal point", "unbalanced layout", "cluttered composition",
                    "confusing perspective", "poor framing"
                ],
                "technique": [
                    "anatomy off", "perspective issues", "overworked rendering", 
                    "color problems", "technical inconsistencies", "execution issues",
                    "needs more practice", "fundamentals need work"
                ],
                "concept": [
                    "unclear narrative", "cliché", "tone mismatch", 
                    "concept unclear", "lacks originality", "missing emotion",
                    "could be more developed", "needs stronger idea"
                ],
                "presentation": [
                    "image quality issues", "poor lighting in photo", "needs better documentation",
                    "crop could be improved", "resolution too low"
                ]
            }
        }

        created_count = 0
        updated_count = 0

        for polarity, categories in SEED_TAGS.items():
            for category, labels in categories.items():
                for label in labels:
                    tag, was_created = Tag.objects.get_or_create(
                        label__iexact=label,
                        defaults={
                            'label': label,
                            'polarity': polarity,
                            'category': category,
                            'is_system': True
                        }
                    )
                    
                    if was_created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Created tag: {polarity}:{label} ({category})')
                        )
                    else:
                        # Update existing tag to ensure consistency
                        if not tag.is_system or tag.category != category or tag.polarity != polarity:
                            tag.is_system = True
                            tag.category = category
                            tag.polarity = polarity
                            tag.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'Updated tag: {polarity}:{label} ({category})')
                            )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding complete! Created {created_count} new tags, updated {updated_count} existing tags.'
            )
        )
        
        # Show tag counts by category and polarity
        pro_count = Tag.objects.filter(polarity=Tag.PRO).count()
        con_count = Tag.objects.filter(polarity=Tag.CON).count()
        
        self.stdout.write(f'Total Pro tags: {pro_count}')
        self.stdout.write(f'Total Con tags: {con_count}')
        
        categories = Tag.objects.values_list('category', flat=True).distinct()
        self.stdout.write(f'Categories: {", ".join(sorted(categories))}')