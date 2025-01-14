from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


# Create your models here.

def user_profile_images_path(instance, filename):
    return f'profile_images/{instance.username}/{filename}'

class User(AbstractUser):
    profile_image = models.ImageField(upload_to=user_profile_images_path, blank=True, null=True)

    def __str__(self):
        return self.username
    

class Profile(models.Model):
    GENDER_CHOICES = (
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}의 프로필"