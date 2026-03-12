from django.shortcuts import render
from .models import Location, Restaurant

def home_page(request):
    return render(request, "core/home.html")
def contact_page(request):
    return render(request, template_name= "core/contact.html")
def profile_page(request):
    return render(request, template_name= "core/profile.html")
def restaurants_page(request):
    restaurants = Restaurant.objects.all()
    return render(request, "core/restaurants.html", {
        "restaurants": restaurants
    })