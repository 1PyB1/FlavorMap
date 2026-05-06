from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class Accounts(admin.ModelAdmin):
    list_display = ("name" , )