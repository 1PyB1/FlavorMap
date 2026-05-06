from django.forms import ModelForm , Form , forms

from .models import UserResponse

class PostUserResponse(ModelForm):
    class Meta():
        model = UserResponse
        fields = ("user", "title", "message_section")