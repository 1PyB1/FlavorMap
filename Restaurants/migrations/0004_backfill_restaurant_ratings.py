from django.db import migrations
from django.db.models import Avg


def backfill_restaurant_ratings(apps, schema_editor):
    Restaurant = apps.get_model("Core", "Restaurant")
    ReviewSystem = apps.get_model("Restaurants", "ReviewSystem")

    for restaurant in Restaurant.objects.all():
        average_rating = (
            ReviewSystem.objects.filter(restaurant_id=restaurant.id).aggregate(avg_rating=Avg("rating"))["avg_rating"]
            or 0
        )
        restaurant.rating = round(average_rating, 1)
        restaurant.save(update_fields=["rating"])


class Migration(migrations.Migration):

    dependencies = [
        ("Core", "0012_rename_profile_userresponse_user"),
        ("Restaurants", "0003_reviewsystem_unique_review_per_user_per_restaurant"),
    ]

    operations = [
        migrations.RunPython(backfill_restaurant_ratings, migrations.RunPython.noop),
    ]
