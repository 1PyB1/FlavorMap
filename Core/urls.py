from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("contact/", views.contact_page, name="contact"),
    path('Accounts/', include("Accounts.urls")),
]
