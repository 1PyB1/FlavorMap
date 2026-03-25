from django.shortcuts import render
from .models import Location, Restaurant, Category
from django.core.paginator import Paginator

def home_page(request):
    return render(request, "core/home.html")
def contact_page(request):
    return render(request, template_name= "core/contact.html")
def profile_page(request):
    return render(request, template_name= "core/profile.html")
def restaurants_page(request):
    restaurants = Restaurant.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    search = request.GET.get('search')

    if category_id:
        restaurants = restaurants.filter(categories=category_id)

    if search:
        restaurants = restaurants.filter(name__icontains=search)

    if search and category_id:
        restaurants = restaurants.filter(categories=category_id, name__icontains=search)

    paginator = Paginator(restaurants, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/restaurants.html', {
        'page_obj': page_obj,
        'categories': categories,
    })
def restaurant_detail(request, id):
    restaurant = Restaurant.objects.get(id=id)

    return render(request,"core/restaurant-detail.html",{
        "restaurant": restaurant
    })