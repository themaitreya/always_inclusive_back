from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    # path('login/', views.login, name='login'),
    # path('logout/', views.logout, name='logout'),
    # path('signup/', views.signup, name='signup'),
    # path('profile/<str:username>', views.profile, name='profile'),
    # path('profile/<str:username>/edit/', views.profile_edit, name='profile_edit'),
    # path('admin/login/', views.admin_login, name='admin_login'),
    # path('admin/users/', views.user_list, name='user_list'),
    # path('delete/', views.delete_account, name='delete'),
    # path('change-language/', views.change_language, name='change_language'),
    # path('profile/update/', views.update_profile, name='update_profile'),
    path('api/login/', views.login_api, name='api_login'),
    path('api/signup/', views.signup_api, name='api_signup'),
    path('api/profile/', views.profile_api, name='api_profile'),
    path('api/profile/<str:username>/', views.get_user_profile, name='api_user_profile'),
    path('api/profile/update/', views.update_profile_api, name='api_profile_update'),

]