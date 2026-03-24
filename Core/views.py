from django.shortcuts import render
from .models import Location, Restaurant
from django.core.paginator import Paginator

def home_page(request):
    return render(request, "core/home.html")
def contact_page(request):
    return render(request, template_name= "core/contact.html")
def profile_page(request):
    return render(request, template_name= "core/profile.html")
def restaurants_page(request):
    restaurants = Restaurant.objects.all()

    paginator = Paginator(restaurants, 6)  # 🔥 sayfa başına 6 restoran

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/restaurants.html', {
        'page_obj': page_obj
        })
def restaurant_detail(request, id):
    restaurant = Restaurant.objects.get(id=id)

    return render(request,"core/restaurant-detail.html",{
        "restaurant": restaurant
    })