from django.db import models
from django.utils import timezone
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
    name = models.CharField(max_length=30)
    description = models.TextField()
    location = models.ForeignKey(Location,on_delete=models.CASCADE )
    date = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0)
    image = models.ImageField(upload_to="restaurants/", null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='restaurants')
    class Meta:
        ordering = ['-date']
    def __str__(self):
        return f"{self.name} - {self.date}"
