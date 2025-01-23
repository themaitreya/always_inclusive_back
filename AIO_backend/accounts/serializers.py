from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)  # 비밀번호 재확인 용
    
    class Meta:
        model = User
        # 프론트에서 보내는 필드에 맞춰 구성
        fields = ['email', 'password', 'password2', 'gender', 'age_group']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return attrs
    
    def create(self, validated_data):
        # password2는 실제 DB 저장할 필드가 아님
        validated_data.pop('password2', None)
        username = validated_data.get('username')
        if not username:  # username이 없다면?
            validated_data['username'] = validated_data['email']  # email로 대체

        # User 인스턴스 생성
        user = User(
            email=validated_data['email'],
            gender=validated_data.get('gender', ''),
            age_group=validated_data.get('age_group', ''),
            username=validated_data.get('username', ''),
        )
        # Django의 set_password()로 비밀번호 해시
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'ott_preference', 'profile_image']
        read_only_fields = ['id', 'username']