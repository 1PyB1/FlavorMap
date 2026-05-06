from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from .models import Profile


def register_page(request):
    if request.user.is_authenticated:
        return redirect("profile")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.create(user=user, name=form.cleaned_data["name"])
        login(request, user)
        return redirect("profile")

    return render(request, "accounts/register.html", {"form": form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect("profile")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("profile")

    return render(request, "accounts/login.html", {"form": form})


@login_required(login_url="login")
def profile_page(request):
    profile = Profile.objects.filter(user=request.user).first()
    if profile is None:
        profile = Profile.objects.create(user=request.user, name=request.user.username)

    favorite_restaurants = request.user.favorite_restaurants.select_related("location").all()
    review_count = profile.reviewsystem_set.count()

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "favorite_restaurants": favorite_restaurants,
            "review_count": review_count,
        },
    )
