# Generated by Django 5.2.1 on 2025-05-15 05:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('critique', '0002_artwork_author_artwork_dimensions_artwork_image_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_artworks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='critique.artwork')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='critique.comment')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
