from django.core.management.base import BaseCommand
from main.models import District, City

class Command(BaseCommand):
    help = 'Populate image_urls field for all districts and cities with random images from tourist spots'

    def handle(self, *args, **kwargs):
        # Update all districts
        districts = District.objects.all()
        for district in districts:
            district.set_random_images()  # Populate image_urls field
            self.stdout.write(self.style.SUCCESS(f'Updated images for district: {district.name}'))

        # Update all cities
        cities = City.objects.all()
        for city in cities:
            city.set_random_images()  # Populate image_urls field
            self.stdout.write(self.style.SUCCESS(f'Updated images for city: {city.name}'))
