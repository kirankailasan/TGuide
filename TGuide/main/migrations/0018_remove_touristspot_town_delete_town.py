# Generated by Django 5.1.5 on 2025-02-01 03:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_touristspot_normalized_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='touristspot',
            name='town',
        ),
        migrations.DeleteModel(
            name='Town',
        ),
    ]
