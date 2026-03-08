from django.contrib import admin
from .models import Location, Restaurant
# Register your models here.
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "location")
    search_fields = ("name", "location__city", "location__district")
    list_filter = ("location__city", "location__district")
    ordering = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "district")
    search_fields = ("city", "district")
    ordering = ("city",)
