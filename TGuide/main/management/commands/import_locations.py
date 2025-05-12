import os
import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import TouristSpot

class Command(BaseCommand):
    help = "Update latitude, longitude, and image URLs for tourist spots using Geoapify API"

    def handle(self, *args, **kwargs):
        api_key = settings.GEOAPIFY_API_KEY
        if not api_key:
            self.stderr.write(self.style.ERROR("Geoapify API key is missing!"))
            return

        base_url = "https://api.geoapify.com/v1/geocode/search"
        
        spots = TouristSpot.objects.filter(latitude__isnull=True, longitude__isnull=True)  # Only update missing data
        total_updated = 0

        for spot in spots:
            query = f"{spot.name}, Kerala, India"
            params = {"text": query, "format": "json", "apiKey": api_key}

            self.stdout.write(f"Processing: {spot.name}")

            # Fetch latitude & longitude
            response = requests.get(base_url, params=params, timeout=60)
            if response.status_code != 200:
                self.stderr.write(self.style.ERROR(f"Failed to fetch location for {spot.name}: {response.text}"))
                continue

            data = response.json()
            if "results" not in data or not data["results"]:
                self.stderr.write(self.style.WARNING(f"No results found for {spot.name}"))
                continue

            result = data["results"][0]
            spot.latitude = result.get("lat")
            spot.longitude = result.get("lon")

            

            # Save the updated tourist spot
            spot.save()
            total_updated += 1

            self.stdout.write(self.style.SUCCESS(f"✅ Updated {spot.name} (Lat: {spot.latitude}, Lon: {spot.longitude})"))

            time.sleep(1)  # Prevent rate limit issues

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {total_updated} tourist spots!"))
