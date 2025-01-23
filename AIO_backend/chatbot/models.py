from django.db import models

class ChatHistory(models.Model):
    email = models.EmailField()
    messages = models.JSONField(default=list)  # 메시지 이력을 JSON으로 저장
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']