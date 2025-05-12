from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import datetime, random
from django.dispatch import receiver
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True)
    state = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username

# Automatically create a Profile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Automatically save the Profile when the User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class PlanTrip(models.Model):
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    start_time = models.DateTimeField(default= timezone.now)
    end_date = models.DateField()
    end_time = models.DateTimeField(blank=True, null = True)
    people = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True) 
    preferences = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Trip to {self.location} for {self.people} people"

class District(models.Model):
    name = models.CharField(max_length=255, unique=True)
    state = models.CharField(max_length=255, default="Kerala")
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(null=True, blank=True)
    image_urls = models.JSONField(default=list, null=True, blank=True)  # Store random image URLs

    def set_random_images(self):
        # Get all tourist spots in this district and fetch image URLs
        tourist_spots = TouristSpot.objects.filter(district=self)
        all_images = []
        
        for spot in tourist_spots:
            if spot.image_urls:
                all_images.extend(spot.image_urls)  # Collect image URLs from tourist spots

        # Pick 5 random images (if there are any)
        if all_images:
            unique_images = list(set(all_images))  # Remove duplicates
            self.image_urls = random.sample(unique_images, min(5, len(unique_images)))  # Get up to 5 random images
        else:
            self.image_urls = []
        self.save()
    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    population = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)  # Foreign key to District
    image_urls = models.JSONField(default=list, null=True, blank=True)  # Store random image URLs

    def set_random_images(self):
        # Get all tourist spots in this city and fetch image URLs
        tourist_spots = TouristSpot.objects.filter(city=self)
        all_images = []

        for spot in tourist_spots:
            if spot.image_urls:
                all_images.extend(spot.image_urls)  # Collect image URLs from tourist spots

        # Pick 5 random images (if there are any)
        if all_images:
            unique_images = list(set(all_images))  # Remove duplicates
            self.image_urls = random.sample(unique_images, min(5, len(unique_images)))  # Get up to 5 random images
        else:
            self.image_urls = []
        self.save()
    
    class Meta:
        unique_together = ('name', 'district')


    def __str__(self):
        return self.name






class TouristSpot(models.Model):
    name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255, unique=True, editable=False, default="")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    population = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)  # Foreign key to District
    address = models.CharField(max_length=600, null=True, blank=True) # Example, adjust as needed
    opening_hours = models.CharField(max_length=255, null=True, blank=True) # Example, could be a TimeField or other
    category = models.CharField(max_length=255, null=True, blank=True) # Example, or ForeignKey to a Category model
    amenities = models.TextField(null=True, blank=True) # Could be a ManyToManyField if multiple amenities are possible
    entrance_fee = models.CharField(max_length=255, null=True, blank=True) # Or a DecimalField if you store numerical fees
    image_urls = models.JSONField(default=list, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)

    
    def save(self, *args, **kwargs):
        self.normalized_name = self.normalize_name(self.name)  # Call the normalization function
        super().save(*args, **kwargs)

    @staticmethod
    def normalize_name(name):  # Normalization function (customize as needed)
        return name.strip().lower().replace(".", "").replace("-", " ")

    def __str__(self):
        return self.name

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    price = models.CharField(max_length=50, null=True, blank=True)
    amenities = models.TextField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name
    

class SavedTripPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.CharField(max_length=100)
    people = models.IntegerField()
    preferences = models.TextField(blank=True, null=True)
    plan_html = models.TextField()
    saved_at = models.DateTimeField(auto_now_add=True)
    selected_hotels = models.JSONField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_started = models.BooleanField(default=False)



    def __str__(self):
        return f"{self.user.username}'s trip to {self.location} ({self.start_date} to {self.end_date})"





from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"