from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Core", "0016_restaurant_owner"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "DROP VIEW IF EXISTS restaurants_rating;",
                """
                DELETE FROM Core_restaurant_favorited_by
                WHERE restaurant_id NOT IN (SELECT id FROM Core_restaurant);
                """,
            ],
            reverse_sql=[
                """
                CREATE VIEW IF NOT EXISTS restaurants_rating AS
                SELECT name, rating
                FROM Core_restaurant;
                """,
            ],
        ),
        migrations.AddField(
            model_name="restaurant",
            name="price_range",
            field=models.CharField(
                choices=[
                    ("\u20ac", "\u20ac Budget"),
                    ("\u20ac\u20ac", "\u20ac\u20ac Moderate"),
                    ("\u20ac\u20ac\u20ac", "\u20ac\u20ac\u20ac Expensive"),
                ],
                default="\u20ac\u20ac",
                max_length=3,
            ),
        ),
        migrations.RunSQL(
            sql="""
                CREATE VIEW IF NOT EXISTS restaurants_rating AS
                SELECT name, rating
                FROM Core_restaurant;
            """,
            reverse_sql="DROP VIEW IF EXISTS restaurants_rating;",
        ),
    ]
