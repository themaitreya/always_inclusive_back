from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2', 'profile_image']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']
        