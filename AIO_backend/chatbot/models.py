from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('system', 'System'),
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.role}] {self.message[:30]}"
