from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from accounts.models import User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")
    

# 2차수정 회원가입 클래스
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'gender', 'age_group')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user

# class SignupSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ('username', 'password', 'password2')

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop('password2')
#         user = User.objects.create_user(**validated_data)
#         return user
# 1차수정 회원가입 클래스
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'last_login')
        


# 2차수정 프로필수정기능 
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'gender', 'age_group')
        read_only_fields = ('email',)  # 이메일은 수정 불가
        
# class ProfileUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name', 'last_name')
#         read_only_fields = ('username',)

#     def validate_email(self, value):
#         user = self.context['request'].user
#         if User.objects.exclude(pk=user.pk).filter(email=value).exists():
#             raise serializers.ValidationError("이미 사용중인 이메일입니다.")
#         return value

