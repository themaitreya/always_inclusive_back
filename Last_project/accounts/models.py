from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User


# Create your models here.

def user_profile_images_path(instance, filename):
    return f'profile_images/{instance.username}/{filename}'

class User(AbstractUser):
    profile_image = models.ImageField(upload_to=user_profile_images_path, blank=True, null=True)
        
    GENDER_CHOICES = (
        ('M', '남성'),
        ('F', '여성'),
    )
    
    AGE_CHOICES = (
        ('10S', '10대'),
        ('20S', '20대'),
        ('30S', '30대'),
        ('40S', '40대'),
        ('50S', '50대'),
        ('60P', '60대 이상'),
    )

    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    age_group = models.CharField(max_length=3, choices=AGE_CHOICES, default='30')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    

# class Profile(models.Model):
#     GENDER_CHOICES = (
#         ('M', '남성'),
#         ('F', '여성'),
#         ('O', '기타'),
#     )
    
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     age = models.IntegerField(null=True, blank=True)
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

#     def __str__(self):
#         return f"{self.user.username}의 프로필"