# Generated by Django 4.0.1 on 2022-01-16 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_rename_hotel_favorite_post_rename_hotel_likes_post'),
    ]

    operations = [
        migrations.RenameField(
            model_name='likes',
            old_name='author',
            new_name='user',
        ),
    ]
