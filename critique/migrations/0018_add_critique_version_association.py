# Generated by Django 5.2.1 on 2025-06-17 13:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('critique', '0017_folder_display_order_alter_artwork_image_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='folder',
            options={'ordering': ['display_order', '-updated_at', '-created_at'], 'verbose_name': 'Portfolio Folder', 'verbose_name_plural': 'Portfolio Folders'},
        ),
        migrations.AddField(
            model_name='critique',
            name='artwork_version',
            field=models.ForeignKey(blank=True, help_text='The specific version of the artwork this critique was written for', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='critiques', to='critique.artworkversion'),
        ),
    ]
