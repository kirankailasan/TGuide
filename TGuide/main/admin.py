from django.contrib import admin
from .models import City, District, TouristSpot, Hotel, SavedTripPlan, Profile, ContactMessage

admin.site.register(City)
admin.site.register(District)

admin.site.register(Profile)
admin.site.register(ContactMessage)

class TouristSpotAdmin(admin.ModelAdmin):
    list_display = ('name', 'normalized_name', 'latitude', 'longitude')
    search_fields = ('name', 'description')

admin.site.register(TouristSpot, TouristSpotAdmin)


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display=("name", "district")

@admin.register(SavedTripPlan)
class SavedTripPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'start_date', 'end_date', 'budget', 'people', 'is_completed','is_started', 'saved_at')
    search_fields = ('user__username', 'location')
    list_filter = ('is_completed', 'start_date', 'end_date')

