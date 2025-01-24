# accounts/urls.py
from django.urls import path
from .views import (
    SignupView,
    LoginAPIView,
    LogoutView,
    ProfileView,
    ProfileUpdateView,
    DeleteUserView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('delete/', DeleteUserView.as_view(), name='delete'),
]
