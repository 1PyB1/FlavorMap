from django.db import models
from django.utils import timezone

class Location(models.Model):
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.city} - {self.district}"
class Restaurant(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    location = models.ForeignKey(Location,on_delete=models.CASCADE )
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date']
    def __str__(self):
        return f"{self.name} - {self.date}"
