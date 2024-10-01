from rest_framework import serializers
from .models import BlacklistedToken


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate_refresh_token(self, value):
        if BlacklistedToken.objects.filter(token=value).exists():
            raise serializers.ValidationError("유효하지 않은 리프레시 토큰입니다.")
        return value
