import os
import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import TouristSpot

class Command(BaseCommand):
    help = "Update latitude, longitude, and image URLs for tourist spots using gomaps.pro API"

    def handle(self, *args, **kwargs):
        api_key = settings.GOMAPS_PRO_API_KEY  # Assuming you set GOMAPS_PRO_API_KEY
        if not api_key:
            self.stderr.write(self.style.ERROR("gomaps.pro API key is missing!"))
            return

        base_url = "https://maps.gomaps.pro/maps/api/place/findplacefromtext/json"
        details_url = "https://maps.gomaps.pro/maps/api/place/details/json"

        spots = TouristSpot.objects.filter(latitude__isnull=True, longitude__isnull=True)
        total_updated = 0

        for spot in spots:
            query = f"{spot.name}, Kerala, India"
            params = {
                "input": query,
                "inputtype": "textquery",
                "fields": "place_id",
                "key": api_key,
            }

            self.stdout.write(f"Processing: {spot.name}")

            # Find Place ID
            try:
                response = requests.get(base_url, params=params, timeout=60)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                data = response.json()

                if "candidates" not in data or not data["candidates"]:
                    self.stderr.write(self.style.WARNING(f"No results found for {spot.name}"))
                    continue

                place_id = data["candidates"][0]["place_id"]

                # Get Place Details (latitude, longitude)
                details_params = {
                    "place_id": place_id,
                    "fields": "geometry",
                    "key": api_key,
                }

                details_response = requests.get(details_url, params=details_params, timeout=60)
                details_response.raise_for_status()
                details_data = details_response.json()

                if "result" not in details_data or "geometry" not in details_data["result"]:
                    self.stderr.write(self.style.WARNING(f"No geometry data found for {spot.name}"))
                    continue

                location = details_data["result"]["geometry"]["location"]
                spot.latitude = location["lat"]
                spot.longitude = location["lng"]

                spot.save()
                total_updated += 1

                self.stdout.write(self.style.SUCCESS(f"✅ Updated {spot.name} (Lat: {spot.latitude}, Lon: {spot.longitude})"))

                time.sleep(1)  # Prevent rate limit issues

            except requests.exceptions.RequestException as e:
                self.stderr.write(self.style.ERROR(f"Failed to fetch location for {spot.name}: {e}"))
                continue
            except KeyError:
                self.stderr.write(self.style.ERROR(f"Failed to fetch location for {spot.name}: Unexpected API response format"))
                continue

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {total_updated} tourist spots!"))