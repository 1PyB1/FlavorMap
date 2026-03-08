from django.db import models

class Location(models.Model):
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.city} - {self.district}"
class Restaurant(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    location = models.ForeignKey(Location,on_delete=models.CASCADE )
    def __str__(self):
        return self.name
