from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_POST, require_http_methods
from .forms import SignupForm, ProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.paginator import Paginator
from django.utils import translation
from django.conf import settings

# Create your views here.

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .serializers import LoginSerializer, SignupSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import ProfileSerializer

# @api_view(['PUT'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def update_profile_api(request):
#     serializer = ProfileUpdateSerializer(request.user, data=request.data, context={'request': request})
#     if serializer.is_valid():
#         serializer.save()
#         return Response({
#             "message": "프로필이 성공적으로 수정되었습니다.",
#             "user": serializer.data
#         })
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def profile_api(request):
#     serializer = ProfileSerializer(request.user)
#     return Response(serializer.data)

# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def get_user_profile(request, username):
#     user = get_object_or_404(User, username=username)
#     serializer = ProfileSerializer(user)
#     return Response(serializer.data)

#회원가입DRF
@api_view(['POST'])
@permission_classes([AllowAny])
def signup_api(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "회원가입이 완료되었습니다.",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#로그인DRF
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# def signup(request):
#     if request.method == 'POST':
#         form = SignupForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save()
#             auth_login(request, user)
#             return redirect('accounts:profile.html')
#     else:
#         form = SignupForm()
#     return render(request, 'accounts/signup.html', {'form': form})

# # @require_http_methods(['GET', 'POST'])
# # def login(request):
# #     if request.method == 'POST':
# #         form = AuthenticationForm(request, request.POST)
# #         if form.is_valid():
# #             auth_login(request, form.get_user())
# #             next_url = request.GET.get('next') or 'index'
# #             return redirect('accounts:profile.html')
# #     else:
# #         form = AuthenticationForm(request)
# #     return render(request, 'accounts/login.html', {'form': form})

# @require_http_methods(['GET', 'POST'])
# def login(request):
#     if request.user.is_authenticated:
#         return redirect('accounts:profile', username=request.user.username)
    
#     if request.method == 'POST':
#         form = AuthenticationForm(request, request.POST)
#         if form.is_valid():
#             auth_login(request, form.get_user())
#             return redirect('accounts:profile.html', username=request.user.username)
#         else:
#             # 로그인 실패 시 에러 메시지를 포함하여 다시 로그인 페이지로
#             messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
#             return render(request, 'accounts/login.html', {'form': form})
#     else:
#         form = AuthenticationForm(request)
#     return render(request, 'accounts/login.html', {'form': form})

# @require_POST
# def logout(request):
#     if request.user.is_authenticated:
#         auth_logout(request)
#     return redirect('accounts:login_api')


# @login_required
# def profile(request, username):
#     profile = get_object_or_404(User, username=username)
    
#     return render(request, 'accounts/profile.html', {'profile': profile})

# def profile_edit(request, username):
#     if request.user.username != username:
#         return redirect('accounts:profile', username=username)
#     user = get_object_or_404(User, username=username)
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, request.FILES, instance=user)
#         if form.is_valid():
#             form.save()
#             return redirect('accounts:profile', username=username)
#     else:
#         form = ProfileForm(instance=user)
#     return render(request, 'accounts/profile_edit.html', {'form': form})




# def is_admin(user):
#     return user.is_staff or user.is_superuser

# @require_http_methods(['GET', 'POST'])
# def admin_login(request):
#     if request.user.is_authenticated:
#         if is_admin(request.user):
#             return redirect('admin:index')
#         else:
#             messages.error(request, '관리자 권한이 없습니다.')
#             auth_logout(request)
#             return redirect('accounts:login')
    
#     if request.method == 'POST':
#         form = AuthenticationForm(request, request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             if is_admin(user):
#                 auth_login(request, user)
#                 return redirect('admin:index')
#             else:
#                 messages.error(request, '관리자 계정으로만 로그인이 가능합니다.')
#                 return render(request, 'accounts/admin_login.html', {'form': form})
#         else:
#             messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
#     else:
#         form = AuthenticationForm()
    
#     return render(request, 'accounts/admin_login.html', {'form': form})


# @user_passes_test(lambda u: u.is_staff)
# def user_list(request):
#     users = User.objects.all().order_by('-date_joined')
#     paginator = Paginator(users, 10)  # 페이지당 10명씩 표시
    
#     page = request.GET.get('page')
#     users = paginator.get_page(page)
    
#     context = {
#         'users': users,
#     }
#     return render(request, 'accounts/user_list.html', context)

# @login_required
# @require_POST
# def delete_account(request):
#     if request.user.is_authenticated:
#         user = request.user
#         user.delete()  # DB에서 사용자 정보 삭제
#         auth_logout(request)  # 로그아웃 처리
#         messages.success(request, '회원탈퇴가 완료되었습니다.')
#         return redirect('accounts:login')
#     return redirect('accounts:login')



# @login_required
# def change_language(request):
#     if request.method == 'POST':
#         language = request.POST.get('language', 'en')
#         if language in [lang[0] for lang in settings.LANGUAGES]:
#             translation.activate(language)
#             request.session[translation.LANGUAGE_SESSION_KEY] = language
        
#         return redirect(request.META.get('HTTP_REFERER', 'accounts:profile'))
    
# # @login_required
# # def update_profile(request):
# #     profile, created = Profile.objects.get_or_create(user=request.user)
    
# #     if request.method == 'POST':
# #         form = ProfileForm(request.POST, instance=profile)
# #         if form.is_valid():
# #             form.save()
# #             messages.success(request, '프로필이 업데이트되었습니다.')
# #             return redirect('accounts:profile', username=request.user.username)
# #     else:
# #         form = ProfileForm(instance=profile)
    
# #     return render(request, 'accounts/update_profile.html', {'form': form})