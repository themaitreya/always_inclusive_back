from django.urls import path
from .views import ChatbotView, ChatbotView_Anonymous

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chatbot_chat'),
    path('chat/anonymous/', ChatbotView_Anonymous.as_view(), name='chatbot_chat_Anonymous'),
]