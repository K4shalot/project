# Generated by Django 5.1.3 on 2024-12-12 11:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blog',
            name='author',
        ),
    ]
