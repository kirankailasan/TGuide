import requests
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import TouristSpot

# Load API credentials from settings.py
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
SEARCH_ENGINE_ID = settings.GOOGLE_CSE_ID

class Command(BaseCommand):
    help = "Fetch and store image URLs for all tourist spots using Google Custom Search API"

    def fetch_image_urls(self, place_name):
        """Fetch first 5 image URLs for a tourist spot using Google Custom Search API."""
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": f"{place_name} tourist attraction",
            "cx": SEARCH_ENGINE_ID,
            "key": GOOGLE_API_KEY,
            "searchType": "image",
            "num": 5,  # Get first 5 images
            "imgSize": "large",  # Fetch high-resolution images
        }

        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [item["link"] for item in data.get("items", []) if "link" in item][:5]
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f"Error fetching images for {place_name}: {e}"))
            return []

    def handle(self, *args, **kwargs):
        """Fetch and update image URLs for all tourist spots in the database."""
        spots = TouristSpot.objects.filter(image_urls=[]) # Get all tourist spots

        for spot in spots:
            self.stdout.write(f"Fetching images for: {spot.name}")
            image_urls = self.fetch_image_urls(spot.name)

            if image_urls:
                spot.image_urls = image_urls
                spot.save()
                self.stdout.write(self.style.SUCCESS(f"✔ Updated images for {spot.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠ No images found for {spot.name}"))

            time.sleep(2)  # Delay to avoid hitting API rate limits

        self.stdout.write(self.style.SUCCESS("✅ Image fetching completed!"))
