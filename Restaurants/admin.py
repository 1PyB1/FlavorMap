from django.contrib import admin
from .models import ReviewSystem


@admin.register(ReviewSystem)
class RestaurantReviews(admin.ModelAdmin):
    list_display = ("title", "restaurant", "user", "rating")
    search_fields = ("title", "review", "restaurant__name", "user__user__username")
