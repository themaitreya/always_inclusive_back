# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'gender', 'age_group']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)

        # username이 비어 있으면 email로 대체
        username = validated_data.get('username', '')
        if not username:
            validated_data['username'] = validated_data['email']

        user = User(
            email=validated_data['email'],
            gender=validated_data.get('gender', ''),
            age_group=validated_data.get('age_group', ''),
            username=validated_data.get('username')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    사용자 프로필 조회/수정 시 사용하는 직렬화기
    """
    class Meta:
        model = User
        # User 모델의 nickname, profile_image 등을 추가로 직렬화
        fields = [
            'id', 'email', 'nickname', 'profile_image', 
            'gender', 'age_group'
        ]
        read_only_fields = ['id', 'email']
