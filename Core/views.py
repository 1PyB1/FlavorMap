from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import PostUserResponse

from .models import UserResponse, Restaurant, Category

def home_page(request):
    featured_restaurants = Restaurant.objects.select_related("location").prefetch_related("categories")[:4]
    latest_restaurants = Restaurant.objects.select_related("location").order_by("-date")[:3]
    category_count = Category.objects.count()
    restaurant_count = Restaurant.objects.count()

    return render(
        request,
        "core/home.html",
        {
            "featured_restaurants": featured_restaurants,
            "latest_restaurants": latest_restaurants,
            "category_count": category_count,
            "restaurant_count": restaurant_count,
        },
    )

@login_required(login_url="/Accounts/login/")
def contact_page(request):
    if request.method == "POST":
        form = PostUserResponse(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            message_section = form.cleaned_data["message_section"]
            profile = request.user.profile
            post = UserResponse(user=profile,title=title , message_section=message_section)
            post.save()
            return HttpResponseRedirect('/contact')
    else:
        form = PostUserResponse()
    return render(request, "core/contact.html", {"form": form})
