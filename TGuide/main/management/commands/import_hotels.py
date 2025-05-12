import csv
import os
from django.core.management.base import BaseCommand
from main.models import Hotel, District  # Import your models

class Command(BaseCommand):
    help = "Import hotels from a CSV file into the database."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs["csv_file"]

        # Check if file exists
        if not os.path.exists(csv_file_path):
            self.stderr.write(self.style.ERROR(f"File '{csv_file_path}' not found."))
            return

        with open(csv_file_path, newline="", encoding="latin1") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Prevent duplicate hotel entries
                if not Hotel.objects.filter(name=row["name"]).exists():
                    district, _ = District.objects.get_or_create(name=row["district"])
                    
                    # Create new hotel entry
                    Hotel.objects.create(
                        name=row["name"],
                        district=district,
                        price=row["price"],
                        amenities=row["amenities"],
                        
                    )
                    self.stdout.write(self.style.SUCCESS(f"Added: {row['name']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Skipped (Already exists): {row['name']}"))

        self.stdout.write(self.style.SUCCESS("CSV Import Completed!"))
