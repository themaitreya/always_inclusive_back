from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model, logout
from rest_framework.authtoken.models import Token

from .serializers import (
    UserSignupSerializer, 
    UserProfileSerializer,
    DeleteAccountSerializer
)

User = get_user_model()

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]  # 회원가입은 인증 안 된 상태에서도 가능

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # (선택) 가입과 동시에 토큰 발급
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
    permission_classes = [AllowAny]  # 로그인은 인증 없이 접근 가능

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

        # 비밀번호 확인
        if not user.check_password(password):
            return Response(
                {"success": False, "message": "비밀번호가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 여기까지 통과하면 로그인 성공
        # (옵션) TokenAuthentication을 쓴다면 토큰 발급/조회
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
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1) 인증된 사용자(토큰으로 인증)의 Token을 삭제
        Token.objects.filter(user=request.user).delete()
        
        # 2) (선택) Django 세션 로그아웃(세션 기반도 함께 쓰는 경우)
        logout(request)
        
        # 3) 응답
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class ProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

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
    Body: { "password": "..." }

    - 토큰 인증 (IsAuthenticated)
    - 비밀번호 확인
    - 맞으면 user.delete()
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