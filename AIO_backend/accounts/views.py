# accounts/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model, logout
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import (
    UserSignupSerializer,
    UserProfileSerializer,
    DeleteAccountSerializer
)

User = get_user_model()


class SignupView(generics.CreateAPIView):
    """
    POST /api/accounts/signup/
    - 회원가입
    """
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 가입과 동시에 Token 발급
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "user_id": user.id,
                "email": user.email,
                "token": token.key
            },
            status=status.HTTP_201_CREATED
        )


class LoginAPIView(APIView):
    """
    POST /api/accounts/login/
    - 로그인
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"success": False, "message": "이메일과 비밀번호를 모두 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "해당 계정이 존재하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(password):
            return Response(
                {"success": False, "message": "비밀번호가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 로그인 성공 -> 토큰 발급
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "success": True,
                "message": "로그인 성공",
                "token": token.key
            },
            status=status.HTTP_200_OK
        )


class LogoutView(generics.GenericAPIView):
    """
    POST /api/accounts/logout/
    - 로그아웃 (Token 삭제)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 현재 사용자의 토큰 삭제
        Token.objects.filter(user=request.user).delete()
        # (선택) Django 세션 로그아웃
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveAPIView):
    """
    GET /api/accounts/profile/
    - 현재 로그인한 사용자의 프로필 조회
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/accounts/profile/update/
    - 현재 로그인한 사용자의 프로필 수정 (nickname, profile_image 등)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    # 이미지 업로드를 위한 파서
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    # PATCH 메서드를 지원하기 위해 아래 메서드 추가 (부분 수정)
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class DeleteUserView(APIView):
    """
    POST /api/accounts/delete/
    {
        "password": "..."
    }
    - 현재 로그인한 사용자 회원탈퇴
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']

        user = request.user
        if not user.check_password(password):
            return Response(
                {"message": "비밀번호가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()
        return Response({"message": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)
