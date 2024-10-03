from rest_framework import serializers
from .models import BlacklistedToken
from django.contrib.auth import get_user_model


class LoginSerializer(serializers.ModelSerializer):
    """
    이 시리얼라이저는 로그인 요청을 처리합니다.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        """
        이 시리얼라이저는 User 모델을 사용합니다.
        """

        model = get_user_model()
        fields = ["email", "password"]


class LogoutSerializer(serializers.ModelSerializer):
    """
    이 시리얼라이저는 로그아웃 요청을 처리합니다.
    """

    refresh_token = serializers.CharField()

    class Meta:
        """
        이 시리얼라이저는 BlacklistedToken 모델을 사용합니다.
        """

        model = BlacklistedToken
        fields = ["refresh_token"]


class RefreshTokenSerializer(serializers.ModelSerializer):
    """
    이 시리얼라이저는 리프레시 토큰을 검증합니다.
    """

    refresh_token = serializers.CharField()

    def validate_refresh_token(self, value):
        if BlacklistedToken.objects.filter(token=value).exists():
            raise serializers.ValidationError("유효하지 않은 리프레시 토큰입니다.")
        return value

    class Meta:
        """
        이 시리얼라이저는 BlacklistedToken 모델을 사용합니다.
        """

        model = BlacklistedToken
        fields = ["refresh_token"]
