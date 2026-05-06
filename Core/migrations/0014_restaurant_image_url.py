from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0013_restaurant_favorited_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
