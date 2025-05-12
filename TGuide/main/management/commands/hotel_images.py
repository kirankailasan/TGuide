import requests
from django.core.management.base import BaseCommand
from main.models import Hotel

# 🔹 Replace with your actual API Key and Custom Search Engine ID (CX)
GOOGLE_API_KEY = "AIzaSyAmsV7HvPyIrpLBhNLOb9zDiBfo0_t9a6s"
SEARCH_ENGINE_ID = "66a9ced681ae14414"

SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


def fetch_hotel_image(hotel_name, district):
    """Fetch hotel image from Google Custom Search API"""
    query = f"{hotel_name}, {district} hotel image"
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "searchType": "image",
        "num": 1,  # Get only the first result
        "safe": "active",
    }

    response = requests.get(SEARCH_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]["link"]  # First image URL
    
    return None


class Command(BaseCommand):
    help = "Fetch and update hotel images using Google Custom Search API."

    def handle(self, *args, **kwargs):
        hotels = Hotel.objects.filter(image_url__isnull=True)  # Only update missing images
        updated_count = 0

        for hotel in hotels:
            district_name = hotel.district.name if hotel.district else ""
            image_url = fetch_hotel_image(hotel.name, district_name)
            
            if image_url:
                hotel.image_url = image_url
                hotel.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Updated: {hotel.name} -> {image_url}"))
                updated_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"❌ No image found for: {hotel.name}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Done! Updated {updated_count} hotels with images."))
