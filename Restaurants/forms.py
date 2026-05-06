from django import forms
from django.forms import ModelForm
from .models import ReviewSystem, RestaurantMenu
from Core.models import Restaurant


class ReviewSystemForm(ModelForm):
    class Meta:
        model = ReviewSystem
        fields = ("title", "review", "rating")

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating


class RestaurantEditForm(ModelForm):
    class Meta:
        model = Restaurant
        fields = ["image", "description", "phone", "website", "opening_hours", "price_range", "categories"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price_range": forms.Select(),
            "categories": forms.CheckboxSelectMultiple(),
        }


class MenuItemForm(ModelForm):
    class Meta:
        model = RestaurantMenu
        fields = ["section", "item_name", "description", "price"]
        widgets = {
            "description": forms.TextInput(),
        }
