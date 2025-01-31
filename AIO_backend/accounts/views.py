# accounts/views.py
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model, logout
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from utils.mail import send_mail_by_domain  # 방금 만든 유틸 함수
import random

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

class PasswordResetSendCodeView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({"success": False, "message": "이메일이 필요합니다."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 1) User 조회
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"success": False, "message": "해당 이메일의 사용자가 없습니다."},
                            status=status.HTTP_404_NOT_FOUND)

        # 2) 인증코드 생성, 저장
        code = str(random.randint(100000, 999999))
        user.set_reset_code(code, expiry_minutes=10)
        
        # 3) 이메일 전송
        subject = "[Always-Inclusive-OTT] 비밀번호 재설정 코드 안내"
        message = f"안녕하세요.\n비밀번호를 재설정하기 위한 인증코드는 [{code}] 입니다.\n10분 안에 인증을 완료해주세요."

        try:
            send_mail_by_domain(subject, message, email)
        except ValueError as ve:
            return Response({"success": False, "message": str(ve)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message": "이메일 전송 중 오류가 발생했습니다."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"success": True, "message": "인증코드 전송 완료!"}, status=status.HTTP_200_OK)


class PasswordResetVerifyCodeView(APIView):
    """
    POST /api/accounts/password_reset/verify_code/
    request: {"code": "사용자가 입력한 6자리 인증코드"}
    response: {"success": True/False, "message": "..."}
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        if not code:
            return Response({"success": False, "message": "인증코드가 필요합니다."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 1) code가 일치하고, 아직 만료되지 않은 User 탐색
        try:
            user = User.objects.get(reset_code=code)
        except User.DoesNotExist:
            return Response({"success": False, "message": "잘못된 코드이거나, 존재하지 않습니다."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 2) 만료시간 확인
        if not user.check_reset_code(code):
            return Response({"success": False, "message": "인증코드가 만료되었거나 일치하지 않습니다."},
                            status=status.HTTP_400_BAD_REQUEST)

        # ★ 실제로는 세션/토큰에 User 식별정보를 저장해서 "이 사용자만 비밀번호를 변경하도록" 하는 방법이 권장됨
        # 여기서는 단순히 "코드만 맞으면 OK" 형태로 반환

        return Response({"success": True, "message": "인증코드 확인이 완료되었습니다."},
                        status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    POST /api/accounts/password_reset/confirm/
    request: {"code": "인증코드", "new_password": "새 비밀번호"}
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        code = request.data.get('code')  # ★ 코드 추가
        new_password = request.data.get('new_password')

        # code와 새 비밀번호 모두 필요
        if not code or not new_password:
            return Response(
                {"success": False, "message": "인증코드와 새 비밀번호가 모두 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # code와 일치하는 유저 찾기
        try:
            user = User.objects.get(reset_code=code)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "올바르지 않은 코드입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.MultipleObjectsReturned:
            return Response(
                {"success": False, "message": "동일한 코드가 여러 사용자에게 할당되어 있습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 만료 시간 체크
        if not user.check_reset_code(code):
            return Response(
                {"success": False, "message": "인증코드가 만료되었거나 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 새 비밀번호 설정
        user.set_password(new_password)
        user.clear_reset_code()

        return Response({"success": True, "message": "비밀번호가 성공적으로 재설정되었습니다."},
                        status=status.HTTP_200_OK)