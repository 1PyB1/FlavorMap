from Core.models import Category, Location, Restaurant
from django.db import models, transaction
from django.db.models import Avg
from Accounts.models import Profile
from django.conf import settings
__all__ = ["Category", "Location", "Restaurant"]

class ReviewSystem(models.Model):
    title = models.CharField(max_length=20)
    review = models.TextField()
    rating = models.IntegerField()
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "user"],
                name="unique_review_per_user_per_restaurant",
            )
        ]

    def __str__(self):
        return f"{self.user}-{self.title}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.update_restaurant_rating()

    def delete(self, *args, **kwargs):
        restaurant = self.restaurant
        with transaction.atomic():
            super().delete(*args, **kwargs)
            self.update_restaurant_rating(restaurant=restaurant)

    def update_restaurant_rating(self, restaurant=None):
        restaurant = restaurant or self.restaurant
        if not restaurant:
            return

        average_rating = restaurant.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0
        restaurant.rating = round(average_rating, 1)
        restaurant.save(update_fields=["rating"])


class ReviewReply(models.Model):
    review = models.ForeignKey(ReviewSystem, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → {self.review}"
class RestaurantMenu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    section = models.CharField(max_length=50, blank=True, help_text="e.g. Starters, Mains, Desserts")
    item_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["section", "item_name"]

    def __str__(self):
        return f"{self.restaurant.name} — {self.section or 'Menu'}: {self.item_name}"
