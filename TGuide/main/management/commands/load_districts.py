import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import TouristSpot, City, District, Town  # Ensure Town model is included

class Command(BaseCommand):
    help = 'Load tourist destinations and update city and district'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(settings.BASE_DIR, 'main', 'spot.csv')

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file_path}'))
            return

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    name = row.get('name', '').strip()
                    city_name = row.get('city', '').strip()
                    district_name = row.get('district', '').strip()
                

                    if not name or not district_name:
                        self.stdout.write(self.style.WARNING(f'Skipping row due to missing data: {row}'))
                        continue

                    # Get district
                    district = District.objects.filter(name=district_name).first()
                    if not district:
                        self.stdout.write(self.style.WARNING(f'District not found: {district_name}, skipping {name}'))
                        continue

                    # Get or create city
                    city = City.objects.filter(name=city_name, district=district).first()
                    town = None

                    if not city:
                        # If city is not found, create or get town instead
                        town, created = Town.objects.get_or_create(name=city_name, district=district)

                    # Update or create tourist spot
                    spot, created = TouristSpot.objects.update_or_create(
                        name=name,
                        defaults={
                            'city': city,
                            'town': town,
                            'district': district,

                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Imported: {name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated: {name} with new city and district'))

                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f'Missing key: {e} in row: {row}'))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing row {row}: {e}'))

        self.stdout.write(self.style.SUCCESS('Import complete.'))
