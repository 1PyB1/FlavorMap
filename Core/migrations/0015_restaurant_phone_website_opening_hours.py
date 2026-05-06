from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0014_restaurant_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='phone',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='website',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='opening_hours',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
