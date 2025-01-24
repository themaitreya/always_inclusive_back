from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    # 성별, 나이대 필드를 추가 (선택 사항, blank=True, null=True 설정)
    gender = models.CharField(max_length=10, blank=True, null=True)     # "male", "female"
    age_group = models.CharField(max_length=10, blank=True, null=True)  # "10s", "20s", etc.

    nickname = models.CharField(max_length=50, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    def __str__(self):
        return self.email