from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from .models import Category, Restaurant, Location
import requests
from django.http import HttpResponse, JsonResponse
from .forms import ReviewSystemForm, RestaurantEditForm, MenuItemForm
from .models import ReviewSystem, ReviewReply, RestaurantMenu

def _build_description(tags):
    return tags.get("description") or ""


_nominatim_cache = {}

def _get_location(tags, lat, lon):
    city     = tags.get("addr:city", "").strip()
    district = (tags.get("addr:district") or tags.get("addr:county", "")).strip()
    area     = (tags.get("addr:suburb") or tags.get("addr:quarter") or tags.get("addr:neighbourhood", "")).strip()

    if not city:
        cache_key = (round(lat, 3), round(lon, 3))
        if cache_key in _nominatim_cache:
            city, district, area = _nominatim_cache[cache_key]
        else:
            try:
                import time
                resp = requests.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params={"lat": lat, "lon": lon, "format": "json"},
                    headers={"User-Agent": "FlavorMap/1.0"},
                    timeout=5,
                )
                addr = resp.json().get("address", {})
                city     = addr.get("city") or addr.get("town") or addr.get("province") or ""
                district = (addr.get("city_district") or addr.get("municipality")
                            or addr.get("district") or addr.get("county") or "")
                area     = addr.get("suburb") or addr.get("quarter") or addr.get("neighbourhood") or ""
                time.sleep(1)
            except Exception:
                city, district, area = "", "", ""
            _nominatim_cache[cache_key] = (city, district, area)

    location, _ = Location.objects.get_or_create(
        city=city or "Bilinmiyor",
        district=district or "Bilinmiyor",
        area=area or "Bilinmiyor",
    )
    return location


def restaurants_page(request):
    restaurants = Restaurant.objects.select_related("location").prefetch_related("categories").all()
    categories = Category.objects.all()

    category_id = request.GET.get("category")
    search = request.GET.get("search")
    favorites = request.GET.get("favorites")
    price_range = request.GET.get("price_range")

    if category_id:
        restaurants = restaurants.filter(categories=category_id)

    if search:
        search = search.strip()
        restaurants = restaurants.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(location__city__icontains=search)
            | Q(location__district__icontains=search)
            | Q(location__area__icontains=search)
            | Q(categories__name__icontains=search)
        ).distinct()

    if price_range:
        restaurants = restaurants.filter(price_range=price_range)
    
    if favorites:
        if request.user.is_authenticated:
            restaurants = restaurants.filter(favorited_by=request.user)
        else:
            restaurants = restaurants.none()

    paginator = Paginator(restaurants, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    favorited_ids = set()
    if request.user.is_authenticated:
        favorited_ids = set(
            request.user.favorite_restaurants.values_list("id", flat=True)
        )

    current_query = request.GET.copy()
    current_query.pop("page", None)
    current_query = current_query.urlencode()

    return render(
        request,
        "restaurants/restaurants.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "favorited_ids": favorited_ids,
            "price_range_choices": Restaurant.PRICE_RANGE_CHOICES,
            "current_query": current_query,
        },
    )


def restaurant_detail(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    user_review = None
    other_reviews = restaurant.reviews.prefetch_related("replies__user")
    is_favorited = False

    if request.user.is_authenticated:
        user_review = restaurant.reviews.filter(user=request.user.profile).first()
        if user_review:
            other_reviews = other_reviews.exclude(id=user_review.id)
        is_favorited = restaurant.favorited_by.filter(id=request.user.id).exists()

    return render(
        request,
        "restaurants/restaurant-detail.html",
        {
            "restaurant": restaurant,
            "user_review": user_review,
            "other_reviews": other_reviews,
            "is_favorited": is_favorited,
        },
    )


@staff_member_required
def fetch_restaurants(request):
    _nominatim_cache.clear()
    lat = 41.0
    lon = 29.0

    query = f"""
[out:json];
(
  node["amenity"="restaurant"](around:2000,{lat},{lon});
  way["amenity"="restaurant"](around:2000,{lat},{lon});
);
out center;
"""

    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
        headers={"User-Agent": "FlavorMap/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    print("COUNT:", len(data.get("elements", [])))

    for place in data["elements"]:
        tags = place.get("tags", {})
        name = tags.get("name", "Restoran")

        latitude = place.get("lat") or place.get("center", {}).get("lat")
        longitude = place.get("lon") or place.get("center", {}).get("lon")

        if not latitude or not longitude:
            continue

        with transaction.atomic():
            location = _get_location(tags, latitude, longitude)
            description = _build_description(tags)

            obj, created = Restaurant.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "location": location,
                    "latitude": latitude,
                    "longitude": longitude,
                }
            )

            phone         = tags.get("phone") or tags.get("contact:phone") or ""
            website       = tags.get("website") or tags.get("contact:website") or ""
            opening_hours = tags.get("opening_hours") or ""

            obj.location = location
            if phone:         obj.phone = phone
            if website:       obj.website = website
            if opening_hours: obj.opening_hours = opening_hours
            stale = ("API'den çekildi", "Açıklama mevcut değil.", "")
            if obj.description in stale or obj.description.startswith("Mutfak:"):
                obj.description = description

            save_fields = ["location", "description"]
            if phone:         save_fields.append("phone")
            if website:       save_fields.append("website")
            if opening_hours: save_fields.append("opening_hours")
            obj.save(update_fields=save_fields)

            cuisine_raw = tags.get("cuisine", "")
            if cuisine_raw:
                for c in cuisine_raw.split(";"):
                    c = c.strip().title()
                    if c:
                        category, _ = Category.objects.get_or_create(name=c)
                        obj.categories.add(category)

        print("CREATED:", created, name)
    return HttpResponse("Restoranlar başarıyla eklendi ✅")
@login_required(login_url="login")
def add_review(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        if ReviewSystem.objects.filter(
            restaurant=restaurant,
            user=request.user.profile,
        ).exists():
            messages.error(request, "You have already posted a review for this restaurant.")
            return redirect("restaurant_detail", id=restaurant_id)

        form = ReviewSystemForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user.profile
            review.restaurant = restaurant
            try:
                with transaction.atomic():
                    review.save()
            except IntegrityError:
                messages.error(request, "You have already posted a review for this restaurant.")
            else:
                messages.success(request, "Your review was published.")
                return redirect("restaurant_detail", id=restaurant_id)

        else:
            messages.error(request, "Please complete the form with valid information.")

    return redirect("restaurant_detail", id=restaurant_id)


@login_required(login_url="login")
def edit_review(request, review_id):
    review = get_object_or_404(ReviewSystem, id=review_id)

    if review.user != request.user.profile:
        messages.error(request, "You can only edit your own review.")
        return redirect("restaurant_detail", id=review.restaurant_id)

    if request.method == "POST":
        form = ReviewSystemForm(request.POST, instance=review)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, "Your review was updated.")
        else:
            messages.error(request, "Please complete the form with valid information.")

    return redirect("restaurant_detail", id=review.restaurant_id)


@login_required(login_url="login")
def delete_review(request, review_id):
    review = get_object_or_404(ReviewSystem, id=review_id)

    if request.method == "POST":
        if review.user == request.user.profile:
            restaurant_id = review.restaurant_id
            with transaction.atomic():
                review.delete()
            messages.success(request, "Your review was deleted.")
            return redirect("restaurant_detail", id=restaurant_id)

        messages.error(request, "You can only delete your own review.")
        return redirect("restaurant_detail", id=review.restaurant_id)

    return redirect("restaurant_detail", id=review.restaurant_id)


@login_required(login_url="login")
def toggle_favorite(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    user = request.user

    if restaurant.favorited_by.filter(id=user.id).exists():
        restaurant.favorited_by.remove(user)
        is_favorited = False
    else:
        restaurant.favorited_by.add(user)
        is_favorited = True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"is_favorited": is_favorited})

    return redirect("restaurant_detail", id=restaurant_id)


@login_required(login_url="login")
def add_reply(request, review_id):
    review = get_object_or_404(ReviewSystem, id=review_id)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            ReviewReply.objects.create(
                review=review,
                user=request.user.profile,
                text=text,
            )

    return redirect("restaurant_detail", id=review.restaurant_id)


@login_required(login_url="login")
def delete_reply(request, reply_id):
    reply = get_object_or_404(ReviewReply, id=reply_id)

    if request.method == "POST" and reply.user == request.user.profile:
        restaurant_id = reply.review.restaurant_id
        reply.delete()
        return redirect("restaurant_detail", id=restaurant_id)

    return redirect("restaurant_detail", id=reply.review.restaurant_id)


def _is_owner(user, restaurant):
    return restaurant.owner_id == user.id


@login_required(login_url="login")
def restaurant_edit(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    if not _is_owner(request.user, restaurant):
        messages.error(request, "You don't have permission to edit this restaurant.")
        return redirect("restaurant_detail", id=id)

    form = RestaurantEditForm(request.POST or None, request.FILES or None, instance=restaurant)
    menu_form = MenuItemForm()

    if request.method == "POST" and "save_details" in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, "Restaurant updated successfully.")
            return redirect("restaurant_edit", id=id)
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, "restaurants/restaurant-edit.html", {
        "restaurant": restaurant,
        "form": form,
        "menu_form": menu_form,
        "menu_items": restaurant.menu_items.all(),
    })


@login_required(login_url="login")
def menu_item_add(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if not _is_owner(request.user, restaurant):
        return redirect("restaurant_detail", id=restaurant_id)

    if request.method == "POST":
        form = MenuItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            with transaction.atomic():
                item.restaurant = restaurant
                item.save()
            messages.success(request, "Menu item added.")
        else:
            messages.error(request, "Please fill in all required fields.")

    return redirect("restaurant_edit", id=restaurant_id)


@login_required(login_url="login")
def menu_item_delete(request, item_id):
    item = get_object_or_404(RestaurantMenu, id=item_id)
    restaurant_id = item.restaurant_id
    if not _is_owner(request.user, item.restaurant):
        return redirect("restaurant_detail", id=restaurant_id)

    if request.method == "POST":
        with transaction.atomic():
            item.delete()
        messages.success(request, "Menu item deleted.")

    return redirect("restaurant_edit", id=restaurant_id)
