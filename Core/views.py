from django.shortcuts import render

def home_page(request):
    return render(request, template_name= "core/home.html")
def contact_page(request):
    return render(request, template_name= "core/contact.html")
def profile_page(request):
    return render(request, template_name= "core/profile.html")
