from django.db import models
from django.utils import timezone
from Accounts.models import Profile
from django.conf import settings
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Location(models.Model):
    city = models.CharField(max_length=100, null=False, blank=False)
    district = models.CharField(max_length=100, null=False, blank=False)
    area = models.CharField(max_length=100, null=True, blank=False)
    def __str__(self):
        return f"{self.city} - {self.district} - {self.area}"
class Restaurant(models.Model):
    PRICE_BUDGET = "€"
    PRICE_MODERATE = "€€"
    PRICE_EXPENSIVE = "€€€"
    PRICE_RANGE_CHOICES = [
        (PRICE_BUDGET, "€ Budget"),
        (PRICE_MODERATE, "€€ Moderate"),
        (PRICE_EXPENSIVE, "€€€ Expensive"),
    ]

    name = models.CharField(max_length=30)
    description = models.TextField()
    location = models.ForeignKey(Location,on_delete=models.CASCADE )
    date = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0)
    image = models.ImageField(upload_to="restaurants/", null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='restaurants')

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    website = models.CharField(max_length=300, null=True, blank=True)
    opening_hours = models.CharField(max_length=200, null=True, blank=True)
    price_range = models.CharField(max_length=3, choices=PRICE_RANGE_CHOICES, default=PRICE_MODERATE)
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_restaurants',
        blank=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='owned_restaurants',
    )

    class Meta:
        ordering = ['-date']
    def __str__(self):
        return f"{self.name} - {self.date}"
class UserResponse(models.Model):
    title = models.CharField(max_length=50)
    message_section = models.TextField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.user}-{self.title}"
