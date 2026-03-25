from django.contrib import admin
from .models import Location, Restaurant, Category
from django.utils.html import format_html
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = ("name", "location", "date")

    readonly_fields = ("image_preview",)

    search_fields = ("name", "location__city", "location__district", "location__area", "date")

    list_filter = ("location__city", "location__district", "location__area" , "date" , "categories")

    ordering = ("name",)

    filter_horizontal = ("categories",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="120" />', obj.image.url)
        return "No Image"

    image_preview.short_description = "Preview"



@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "district" , "area")
    search_fields = ("city", "district", "area")
    ordering = ("city",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
