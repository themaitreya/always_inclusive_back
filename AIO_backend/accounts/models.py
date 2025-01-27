from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime

class User(AbstractUser):
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, blank=True, null=True)     # "male", "female"
    age_group = models.CharField(max_length=10, blank=True, null=True)  # "10s", "20s", etc.

    nickname = models.CharField(max_length=50, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # 추가: 챗봇 이미지 필드
    chatbot_image = models.ImageField(upload_to='chatbots/', blank=True, null=True)
    
    # ★ 비밀번호 재설정용 코드 & 만료시간
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    reset_code_expires = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.email
    
    def set_reset_code(self, code, expiry_minutes=10):
        """랜덤으로 생성된 인증코드와 만료시간을 설정"""
        self.reset_code = code
        self.reset_code_expires = timezone.now() + datetime.timedelta(minutes=expiry_minutes)
        self.save()

    def check_reset_code(self, code):
        """코드 일치 & 만료시간 이내인지 확인"""
        if self.reset_code != code:
            return False
        if not self.reset_code_expires or timezone.now() > self.reset_code_expires:
            return False
        return True

    def clear_reset_code(self):
        """인증 코드 및 만료시간 제거"""
        self.reset_code = None
        self.reset_code_expires = None
        self.save()