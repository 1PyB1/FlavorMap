from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0015_restaurant_phone_website_opening_hours'),
        ('Restaurants', '0005_reviewreply'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestaurantMenu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(blank=True, help_text='e.g. Starters, Mains, Desserts', max_length=50)),
                ('item_name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='Core.restaurant')),
            ],
            options={
                'ordering': ['section', 'item_name'],
            },
        ),
    ]
