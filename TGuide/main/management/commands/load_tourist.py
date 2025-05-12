import csv
import os
from django.core.management.base import BaseCommand
from main.models import TouristSpot, City, District

class Command(BaseCommand):
    help = "Import tourist spots from a CSV file"

    def handle(self, *args, **kwargs):
        file_path = os.path.join("main", "spot.csv")  # Path to CSV file

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR("CSV file not found!"))
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, quotechar='"', skipinitialspace=True)  # Handles quotes properly
            total_imported = 0

            for row in reader:
                name = row.get("name", "").strip()
                description = row.get("description", "").strip()
                opening_hours = row.get("opening_hours", "").strip()
                amenities = row.get("amenities", "").strip()
                entrance_fee = row.get("entrance_fee", "").strip()
                city_name = row.get("city", "").strip()
                
                district_name = row.get("district", "").strip()

                # Find or create related City and District
                city = City.objects.filter(name__iexact=city_name).first()
                if not city:
                    town_name=city_name
                else:
                    town_name=""

                district = District.objects.filter(name__iexact=district_name).first() if district_name else None

                # Save to database
                TouristSpot.objects.update_or_create(
                    name=name,
                    defaults={
                        "description": description,
                        "opening_hours": opening_hours,
                        "amenities": amenities,
                        "entrance_fee": entrance_fee,
                        "city": city,
                        "district": district,
                        'town': town_name,
                    }
                )

                total_imported += 1

            self.stdout.write(self.style.SUCCESS(f"✅ Successfully imported {total_imported} tourist spots!"))
