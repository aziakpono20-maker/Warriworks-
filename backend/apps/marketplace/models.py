from django.conf import settings
from django.db import models

class ServiceCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=240, blank=True)
    icon_key = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class ArtisanProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='artisan_profile')
    display_name = models.CharField(max_length=120)
    skill = models.CharField(max_length=100)
    location = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    phone_public = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, default='pending')
    profile_image = models.ImageField(upload_to='artisans/profiles/', blank=True)
    portfolio = models.JSONField(default=list, blank=True)
    years_experience = models.PositiveSmallIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.display_name
