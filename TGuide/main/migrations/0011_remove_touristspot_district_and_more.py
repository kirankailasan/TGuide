# Generated by Django 5.1.5 on 2025-01-31 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_remove_touristspot_image_url_touristspot_district_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='touristspot',
            name='district',
        ),
        migrations.RemoveField(
            model_name='touristspot',
            name='entrance_fee',
        ),
        migrations.RemoveField(
            model_name='touristspot',
            name='image_urls',
        ),
        migrations.RemoveField(
            model_name='touristspot',
            name='opening_hours',
        ),
        migrations.RemoveField(
            model_name='touristspot',
            name='population',
        ),
        migrations.AddField(
            model_name='touristspot',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='touristspot',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='touristspot',
            name='category',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AlterField(
            model_name='touristspot',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
