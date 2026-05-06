from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_page, name="register"),
    path("login/", views.login_page, name="login"),
    path("profile/", views.profile_page, name="profile"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]
