from django.core.management.base import BaseCommand
from main.models import TouristSpot  # Replace with your model name
import csv

class Command(BaseCommand):
    help = 'Export TouristSpot data to CSV'

    def handle(self, *args, **options):
        with open('exported_tourist_spots.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'address']  # Replace with actual field names
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for spot in TouristSpot.objects.all():
                # Handle potential encoding issues
                row = {
                    'name': spot.name.encode('utf-8').decode('utf-8'),  # Ensure string is valid UTF-8
                    'address': spot.address.encode('utf-8').decode('utf-8'),
                    
                }
                writer.writerow(row)

        self.stdout.write(self.style.SUCCESS('TouristSpot data exported successfully to exported_tourist_spots.csv'))