from django.urls import path

from . import views
from .views import add_review, delete_review, edit_review, toggle_favorite, add_reply, delete_reply

urlpatterns = [
    path("", views.restaurants_page, name="restaurants"),
    path("<int:id>/", views.restaurant_detail, name="restaurant_detail"),
    path("<int:id>/edit/", views.restaurant_edit, name="restaurant_edit"),
    path("fetch-restaurants/", views.fetch_restaurants),
    path("add-review/<int:restaurant_id>/", add_review, name="add_review"),
    path("edit-review/<int:review_id>/", edit_review, name="edit_review"),
    path("delete-review/<int:review_id>/", delete_review, name="delete_review"),
    path("favorite/<int:restaurant_id>/", toggle_favorite, name="toggle_favorite"),
    path("add-reply/<int:review_id>/", add_reply, name="add_reply"),
    path("delete-reply/<int:reply_id>/", delete_reply, name="delete_reply"),
    path("menu/add/<int:restaurant_id>/", views.menu_item_add, name="menu_item_add"),
    path("menu/delete/<int:item_id>/", views.menu_item_delete, name="menu_item_delete"),
]
