from django.contrib import admin
from .models import Location, Restaurant, Category , UserResponse
from django.utils.html import format_html
from Restaurants.models import ReviewSystem, RestaurantMenu


class ReviewSystemInline(admin.TabularInline):
    model = ReviewSystem
    extra = 0
    fields = ("title", "rating", "user", "review")
    show_change_link = True


class RestaurantMenuInline(admin.TabularInline):
    model = RestaurantMenu
    extra = 1
    fields = ("section", "item_name", "description", "price")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = ("name", "location", "price_range", "owner", "date")
    list_editable = ("price_range",)

    readonly_fields = ("image_preview",)

    search_fields = ("name", "location__city", "location__district", "owner__username")

    list_filter = ("price_range", "location__city", "location__district", "location__area" , "date" , "categories", )

    ordering = ("name",)

    filter_horizontal = ("categories",)
    inlines = (RestaurantMenuInline, ReviewSystemInline,)
    fields = (
        "name",
        "location",
        "owner",
        "price_range",
        "rating",
        "description",
        "image",
        "image_preview",
        "image_url",
        "phone",
        "website",
        "opening_hours",
        "categories",
        "latitude",
        "longitude",
    )

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
@admin.register(UserResponse)
class UserResponseInterface(admin.ModelAdmin):
    list_display = ("title",)
