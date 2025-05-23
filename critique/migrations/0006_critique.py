# Generated by Django 5.2.1 on 2025-05-16 01:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('critique', '0005_profile_profile_picture_url_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Critique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Critique content - analysis of the artwork')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('composition_score', models.PositiveSmallIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], help_text='Rating for composition (1-10)', null=True)),
                ('technique_score', models.PositiveSmallIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], help_text='Rating for technique execution (1-10)', null=True)),
                ('originality_score', models.PositiveSmallIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], help_text='Rating for originality/creativity (1-10)', null=True)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='critiques', to='critique.artwork')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='critiques', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Critique',
                'verbose_name_plural': 'Critiques',
                'ordering': ['-created_at'],
            },
        ),
    ]
