# accounts/urls.py
from django.urls import path
from .views import (
    SignupView,
    LoginAPIView,
    LogoutView,
    ProfileView,
    ProfileUpdateView,
    DeleteUserView,
    
    PasswordResetSendCodeView,
    PasswordResetVerifyCodeView,
    PasswordResetConfirmView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('delete/', DeleteUserView.as_view(), name='delete'),
    
    # 비밀번호 재설정
    path('password_reset/send_code/', PasswordResetSendCodeView.as_view(), name='password_reset_send_code'),
    path('password_reset/verify_code/', PasswordResetVerifyCodeView.as_view(), name='password_reset_verify_code'),
    path('password_reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
